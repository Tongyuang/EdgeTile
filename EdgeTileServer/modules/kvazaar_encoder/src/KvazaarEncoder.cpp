/*
 * @Author: Xu Wang
 * @Date: Sunday, November 17th 2019
 * @Email: wangxu.93@hotmail.com
 * @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
 */
#include <pthread.h>
#include <sys/stat.h>
#include <arpa/inet.h>
#include "precomp.hpp"
#include <chrono>
#include <ctime>

using namespace cv::kvazaar_encoder;

const kvz_api* KvazaarEncoder::kvz_api_instance = NULL;
void (*KvazaarEncoder::writeDataCallbackPtr)(int, uint8_t *, int) = NULL;
std::mutex* KvazaarEncoder::writeDataLock = new std::mutex();
FILE** KvazaarEncoder::outputHandlers = NULL;
EncodeMode KvazaarEncoder::mode = UNSET_MODE;
cv::String KvazaarEncoder::filePrefix = cv::String();
cv::String KvazaarEncoder::serverAddr = cv::String();
int KvazaarEncoder::serverPort = 0;
int KvazaarEncoder::tileCount = 0;
int KvazaarEncoder::tileWidth = 0;
int KvazaarEncoder::tileHeight = 0;
int KvazaarEncoder::videoWidth = 0;
int KvazaarEncoder::videoHeight = 0;
int KvazaarEncoder::sock = 0;
cv::String KvazaarEncoder::videoName=cv::String();
bool KvazaarEncoder::hasSendVideoHeader = false;
FILE* KvazaarEncoder::logHandler = NULL;

long long getNowTime()
{
    std::chrono::milliseconds ms = std::chrono::duration_cast< std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch());
    return ms.count();
}

void KvazaarEncoder::initStatus()
{
    this->frameReadNum = 0;
    this->frameEncodeNum = 0;

    this->inRawFrame = NULL;
    this->rawFrameSemaphore = new Semaphore(0);
    
    if (!this->rawFrameSemaphore){
        fprintf(stderr, "init semaphore failed!\n");
        exit(0);
    }
    
    this->encodeStatus = 0;
}

void KvazaarEncoder::writeData(int frame_id, int tile_id, void *chunk_data)
{
    writeDataLock->lock();
    kvz_data_chunk *chunks_out = (kvz_data_chunk *)chunk_data;
    if (chunks_out != NULL)
    {
        int written = 0;
        // Write data into the output file.
        for (kvz_data_chunk *chunk = chunks_out;
             chunk != NULL;
             chunk = chunk->next)
        {
            written += chunk->len;
        }
        uint8_t* data = (uint8_t*)malloc(sizeof(uint8_t) * written);
        int n = 0;
        for (kvz_data_chunk *chunk = chunks_out;
             chunk != NULL;
             chunk = chunk->next)
        {
            memcpy(data + n, chunk->data, chunk->len);
            n += chunk->len;
        }
        long long now = getNowTime();
        char logContent[256];
        sprintf(logContent, "tile_send_start frame: %d tile: %d size: %d time: %lld\n", frame_id, tile_id, written, now);
        fwrite(logContent, sizeof(char), strlen(logContent), logHandler);
        fflush(logHandler);
        //assert(written + chunk->len <= len_out);
        switch (mode) {
            case LOCAL_FILE_MODE:
            {
                write_data_to_file(frame_id, tile_id, data, written);
                break;
            }
            case SERVER_MODE:
            {
                write_data_to_sock(frame_id, tile_id, data, written);
                break;
            }
            default:
                break;
        }
        now = getNowTime();
        
        sprintf(logContent, "tile_send_end frame: %d tile: %d size: %d time: %lld\n", frame_id, tile_id, written, now);
        fwrite(logContent, sizeof(char), strlen(logContent), logHandler);
        fflush(logHandler);
        free(data);
        kvz_api_instance->chunk_free(chunks_out);
    }
    writeDataLock->unlock();
}

void KvazaarEncoder::write_data_to_file(int frame_id, int tile_id, u_int8_t *data, int len)
{
    //fprintf(stdout, "tile: %d %d\n", tile_id, len);
    if (tile_id < 0)
    {
        for (int i = 0; i < tileCount; i++)
        {
            if (fwrite(data, sizeof(uint8_t), len, outputHandlers[i]) != (size_t)len)
            {
                fprintf(stderr, "Failed to write data to file.\n");
            }
            fflush(outputHandlers[i]);
        }
    }
    else
    {
        if (fwrite(data, sizeof(uint8_t), len, outputHandlers[tile_id]) != (size_t)len)
        {
            fprintf(stderr, "Failed to write data to file.\n");
        }
        fflush(outputHandlers[tile_id]);
    }
}

void KvazaarEncoder::write_data_to_sock(int frame_id, int tile_id, u_int8_t *data, int len)
{
    if(hasSendVideoHeader== false)
    {
        int params_len = 5;
        int* video_params = (int*) malloc(sizeof(int) * params_len);
        video_params[0] = tileWidth;
        video_params[1] = tileHeight;
        video_params[2] = videoWidth;
        video_params[3] = videoHeight;
        video_params[4] = (int)videoName.size();
        send(sock, video_params, sizeof(int) * params_len, 0);
        send(sock, videoName.data(), video_params[4], 0);
        hasSendVideoHeader = true;
        free(video_params);
    }
    
    //fprintf(stdout, "tile: %d %d\n", tile_id, len);
    int32_t header[3];
    header[0] = frame_id;
    header[1] = tile_id;
    header[2] = len;
    send(sock, header, sizeof(int32_t) * 3, 0);
    //assert(n==sizeof(int32_t) * 3);
    int send_n = 0;
    
    while(send_n<len){
        long n = send(sock, data+send_n, len - send_n, 0);
        if(n < 0)
        {
            fprintf(stderr, "socket() failed: %s\n", strerror(errno));
            break;
        }
        else{
            send_n += n;
        }
        
        //fprintf(stdout, "sock: %d, %ld, %d\n", sock, n, len);
    }
    // std::string now = getNowTime();
    // char logContent[256];
    // sprintf(logContent, "send finish frame: %d tile: %d time: %s\n", frame_id, tile_id, now.data());
    // fwrite(logContent, sizeof(char), strlen(logContent), logHandler);
    //fprintf(stdout, "sock: %d, %d\n", send_n, len);
}

bool KvazaarEncoder::open(int width, int height, int gopSize, const char* tile_split, int nthreads, const char* quality)
{
    this->kvz_encoder_instance = NULL;
    this->kvz_api_instance = kvz_api_get(8);
    this->kvz_config_instance = this->kvz_api_instance->config_alloc();

    this->kvz_api_instance->config_init(this->kvz_config_instance);
    this->kvz_api_instance->config_parse(this->kvz_config_instance, "qp", quality);
    this->kvz_api_instance->config_parse(this->kvz_config_instance, "preset", "ultrafast");
    this->kvz_api_instance->config_parse(this->kvz_config_instance, "tiles", tile_split);
    this->kvz_api_instance->config_parse(this->kvz_config_instance, "slices", "tiles");
    this->kvz_api_instance->config_parse(this->kvz_config_instance, "mv-constraint", "frametilemargin");
    //this->kvz_api_instance->config_parse(this->kvz_config_instance, "tiles-encoding-priority", "3,5");
    this->tileCount = this->kvz_config_instance->tiles_width_count * this->kvz_config_instance->tiles_height_count;
    this->tileWidth = this->kvz_config_instance->tiles_width_count;
    this->tileHeight = this->kvz_config_instance->tiles_height_count;
    this->videoWidth = width;
    this->videoHeight = height;
    const char* logFileName = "data/log/encoder.log";
    fprintf(stdout, "log file: %s", logFileName);
    logHandler = fopen(logFileName, "w+");
    
    switch (mode) {
        case LOCAL_FILE_MODE:
        {
            this->outputHandlers = (FILE**)malloc(sizeof(FILE*) * tileCount);
                
            for(int i = 0; i < tileCount; i ++)
            {
                char filename[256];
                sprintf(filename, "%s_%d.hevc",filePrefix.data(), i);
                fprintf(stdout, "%s", filename);
                this->outputHandlers[i] = fopen(filename, "wb");
                if(this->outputHandlers[i] == NULL){
                    fprintf(stderr, "open file error\n");
                    return false;
                }
            }
            break;
        }
        case SERVER_MODE:
        {
             struct sockaddr_in serv_addr;
             if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
             {
                 fprintf(stderr, "Socket creation error \n");
                 return false;
             }
            
             serv_addr.sin_family = AF_INET;
             serv_addr.sin_port = htons(serverPort);
            
             // Convert IPv4 and IPv6 addresses from text to binary form
             if(inet_pton(AF_INET, serverAddr.data(), &serv_addr.sin_addr)<=0)
             {
                 fprintf(stderr, "Address not supported \n");
                 return false;
             }
            
             if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
             {
                 fprintf(stderr, "Connection Failed \n");
                 return false;
             }
            fprintf(stdout, "connect to server\n");
            break;
        }
        default:
        {
            fprintf(stderr, "You should set mode first");
            return false;
        }
    }
    
    
   
    //kvz_config_instance->width = 720;
    //kvz_config_instance->height = 1280;
    this->kvz_config_instance->width = width;
    this->kvz_config_instance->height = height;
    // kvz_config_instance->intra_period = 10;
    this->kvz_config_instance->intra_period = gopSize;
    //config->vps_period = 1;
    this->kvz_config_instance->owf = 0;

    //config->qp = 32;
    this->kvz_config_instance->threads = nthreads;
    this->kvz_config_instance->framerate_num = 30;
    this->kvz_config_instance->framerate_denom = 1;

    this->kvz_encoder_instance = kvz_api_instance->encoder_open(this->kvz_config_instance, this->writeData);

    if (!this->kvz_encoder_instance)
    {
        fprintf(stderr, "Failed to open encoder.\n");
        return false;
    }
    //this->writeDataCallbackPtr = func_ptr;
    fprintf(stdout, "KvazaarEncoder Start.\n");
    return true;
}

void* KvazaarEncoder::run(void* context)
{
    KvazaarEncoder* encoder = (KvazaarEncoder*)context;
    for (;;)
    {
        // 等待有图片输入
        if (encoder->encodeStatus)
        {
            encoder->inRawFrame = NULL;
            encoder->rawFrameSemaphore->Wait();
        }
        encoder->rawFrameLock.lock();

        kvz_picture *cur_in_img = encoder->inRawFrame;
        
        encoder->rawFrameLock.unlock();

        if (cur_in_img)
        {
            cur_in_img->pts = encoder->frameReadNum;
        }
        encoder->frameReadNum++;
        kvz_data_chunk *chunks_out = NULL;
        kvz_picture *img_rec = NULL;
        kvz_picture *img_src = NULL;
        uint32_t len_out = 0;
        kvz_frame_info info_out;
        // current time
        if(cur_in_img)
        {
            long long now = getNowTime();
            char logContent[256];
            sprintf(logContent, "feed frame: %d time: %lld\n", cur_in_img->origin_frame_id, now);
            fwrite(logContent, sizeof(char), strlen(logContent), encoder->logHandler);
            fflush(encoder->logHandler);
        }
        if (!encoder->kvz_api_instance->encoder_encode(encoder->kvz_encoder_instance,
                                                    cur_in_img,
                                                    &chunks_out,
                                                    &len_out,
                                                    &img_rec,
                                                    &img_src,
                                                    &info_out))
        {
            fprintf(stderr, "Failed to encode image.\n");
            encoder->kvz_api_instance->picture_free(cur_in_img);
        }

        if (chunks_out == NULL && cur_in_img == NULL && encoder->kvz_api_instance->frames_read(encoder->kvz_encoder_instance) - encoder->kvz_api_instance->frames_write(encoder->kvz_encoder_instance) == 0)
        {
            // We are done since there is no more input and output left.
            encoder->kvz_api_instance->config_destroy(encoder->kvz_config_instance);
            encoder->kvz_api_instance->encoder_close(encoder->kvz_encoder_instance);
            fprintf(stdout, "KvazaarEncoder Exit.\n");
            encoder->encodeStatus = -1;
            fclose(logHandler);
            switch (encoder->mode) {
                case LOCAL_FILE_MODE:
                {
                    int tiles_count = encoder->kvz_config_instance->tiles_width_count * encoder->kvz_config_instance->tiles_height_count;
                    for(int i = 0; i < tiles_count; i ++)
                    {

                        fclose(outputHandlers[i]);
                    }
                    
                }
                    break;
                case SERVER_MODE:
                {
                    int32_t header[3];
                    header[0] = -1;
                    header[1] = -1;
                    header[2] = -1;
                    send(sock, header, sizeof(int32_t) * 3, 0);
                    shutdown(sock, SHUT_RDWR);
                    //close(sock);
                }
                    break;
                default:
                    break;
            }
            
            return NULL;
        }
        encoder->kvz_api_instance->picture_free(cur_in_img);
        encoder->kvz_api_instance->chunk_free(chunks_out);
        encoder->kvz_api_instance->picture_free(img_rec);
        encoder->kvz_api_instance->picture_free(img_src);
    }
    return NULL;
}

bool KvazaarEncoder::start(int width, int height, int gopSize, String& tile_split, int nthreads, String& quality)
{
    this->initStatus();
    this->encodeStatus = this->open(width, height, gopSize, tile_split.data(), nthreads, quality.data());
    if (!encodeStatus)
    {
        return false;
    }
    pthread_t tid;
    int ret = pthread_create(&tid, NULL, &KvazaarEncoder::run, this);
    if (ret != 0)
    {
        fprintf(stderr, "pthread create failed, error code: %d", ret);
    }

    return encodeStatus;
}

EncoderResult KvazaarEncoder::encode(InputArray y, InputArray u, InputArray v, int frame_idx)
{
    EncoderResult res;
    if (encodeStatus)
    {
        rawFrameLock.lock();
        if (inRawFrame == NULL)
        {
            int ylen = kvz_config_instance->width * kvz_config_instance->height;
            int ulen = ylen / 4;
            int vlen = ylen / 4;
            kvz_picture* img = this->alloc_pic();
            memcpy(img->y, y.getMat().data, ylen);
            memcpy(img->u, u.getMat().data, ulen);
            memcpy(img->v, v.getMat().data, vlen);
            img->origin_frame_id = frame_idx;
            inRawFrame = img;
            this->rawFrameSemaphore->Signal();
            res.encoderState = 1;
            res.frameRead = this->kvz_api_instance->frames_read(this->kvz_encoder_instance);
            res.frameWrite = this->kvz_api_instance->frames_write(this->kvz_encoder_instance);
        }
        else
        {
            res.encoderState = 0;
            res.frameRead = this->kvz_api_instance->frames_read(this->kvz_encoder_instance);
            res.frameWrite = this->kvz_api_instance->frames_write(this->kvz_encoder_instance);
            //printf("seg5\n");
        }
        rawFrameLock.unlock();
    }
    return res;
}

void KvazaarEncoder::stop()
{
    encodeStatus = false;
    rawFrameLock.lock();
    inRawFrame = NULL;
    this->rawFrameSemaphore->Signal();
    rawFrameLock.unlock();
}

kvz_picture* KvazaarEncoder::alloc_pic(){
    return kvz_api_instance->picture_alloc(kvz_config_instance->width, kvz_config_instance->height);
}

int KvazaarEncoder::getEncodeStatus(){
    return this->encodeStatus;
}

bool KvazaarEncoder::setFileMode(String& filename)
{
    mode = LOCAL_FILE_MODE;
    filePrefix = filename;
    return true;
}
bool KvazaarEncoder::setServerMode(String& server_addr, int port)
{
    mode = SERVER_MODE;
    serverAddr = server_addr;
    serverPort = port;
    return true;
}

int KvazaarEncoder::setEncodingPriority(String& priority)
{
    return this->kvz_api_instance->set_encoding_priority(this->kvz_encoder_instance, priority.data());
}
