//
//  OpenHEVCDecoder.cpp
//  HEVCDecoder
//
//  Created by Xu Wang on 2019/11/19.
//  Copyright © 2019 Xu Wang. All rights reserved.
//
#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>
#include <queue>
#include <vector>
#include <math.h>
#include <openHevcWrapper.h>
#include <chrono>
#include "precomp.hpp"

#define CEILDIV(x,y) (((x) + (y) - 1) / (y))
#define     AV_NOPTS_VALUE   ((int64_t)UINT64_C(0x8000000000000000))
using namespace cv::openhevc_decoder;

long long getNowTime()
{
    std::chrono::milliseconds ms = std::chrono::duration_cast< std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch());
    return ms.count();
}

FrameTile OpenHEVCDecoder::read()
{
    if(this->status==DECODER_RUN)
    {
        this->frameVectorSemaphore->Wait();
        FrameTile fObj = *(this->decodedFrames.front());
        this->decodedFrames.pop();
        return fObj;
    }
    else
    {
        FrameTile fobj;
        fobj.frame_id = -1;
        fobj.tile_id  = -1;
        return fobj;
    }
}

VideoProperty OpenHEVCDecoder::readVideoProperty()
{
    if(this->videoPropertySemaphore){
        this->videoPropertySemaphore->Wait();
    }
    delete this->videoPropertySemaphore;
    this->videoPropertySemaphore = NULL;
    return this->videoProperty;
}


bool OpenHEVCDecoder::start(int port)
{
    //this->frameVectorSemaphore = NULL;
    printf("start decoder...\n");
    this->frameVectorSemaphore = new Semaphore(0);
    this->videoPropertySemaphore = new Semaphore(0);
    if ((!this->frameVectorSemaphore) || (! this->videoPropertySemaphore)){
        fprintf(stderr, "init semaphore failed!\n");
        exit(0);
    }
    this->port = port;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    int opt = 1;
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)))
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(this->port);
    
    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address))<0)
    {
        return false;
    }
    fprintf(stdout, "bind to port: %d\n", port);
    
    if (listen(server_fd, 3) < 0)
    {
        return false;
    }
    printf("start listen to port: %d\n", port);
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen))<0)
    {
        return false;
    }
    fprintf(stdout, "accept %d\n", new_socket);
    pthread_t tid;
    int ret = pthread_create(&tid, NULL, &OpenHEVCDecoder::run, this);
    if (ret != 0)
    {
        fprintf(stderr, "pthread create failed, error code: %d", ret);
    }
    return true;
}

void OpenHEVCDecoder::output_file(OpenHEVCDecoder* decoder, int frame_id, int tile_id)
{
    long long now = getNowTime();
    char logContent[256];
    sprintf(logContent, "tile_decode frame: %d tile: %d time: %lld\n", frame_id, tile_id, now);
    fwrite(logContent, sizeof(char), strlen(logContent), decoder->logHandler);
    fflush(decoder->logHandler);
    FrameTile* fObj = new FrameTile();
    if(frame_id == -1 and tile_id == -1)
    {
        decoder->frameVectorLock.lock();
        fObj->frame_id = frame_id;
        fObj->tile_id = tile_id;
        Mat tmp;
        fObj->rawImage = tmp;
        decoder->decodedFrames.push(fObj);
        decoder->frameVectorSemaphore->Signal();
        decoder->frameVectorLock.unlock();
        return;
    }

    libOpenHevcGetPictureInfo(decoder->handlers[tile_id], &decoder->openHevcFrame.frameInfo);
    int format = decoder->openHevcFrame.frameInfo.chromat_format == YUV420 ? 1 : 0;
    libOpenHevcGetPictureInfo(decoder->handlers[tile_id], &decoder->openHevcFrameCpy.frameInfo);
    if(decoder->openHevcFrameCpy.pvY == NULL){
        decoder->openHevcFrameCpy.pvY = calloc (decoder->openHevcFrameCpy.frameInfo.nYPitch * decoder->openHevcFrameCpy.frameInfo.nHeight, sizeof(unsigned char));
        decoder->openHevcFrameCpy.pvU = calloc (decoder->openHevcFrameCpy.frameInfo.nUPitch * decoder->openHevcFrameCpy.frameInfo.nHeight >> format, sizeof(unsigned char));
        decoder->openHevcFrameCpy.pvV = calloc (decoder->openHevcFrameCpy.frameInfo.nVPitch * decoder->openHevcFrameCpy.frameInfo.nHeight >> format, sizeof(unsigned char));
    }
    libOpenHevcGetOutputCpy(decoder->handlers[tile_id], 1, &decoder->openHevcFrameCpy);
    
    int y_len = sizeof(uint8_t) * decoder->openHevcFrameCpy.frameInfo.nYPitch * decoder->openHevcFrameCpy.frameInfo.nHeight;
    int u_len = sizeof(uint8_t) * decoder->openHevcFrameCpy.frameInfo.nUPitch * decoder->openHevcFrameCpy.frameInfo.nHeight >> format;
    int v_len = sizeof(uint8_t) * decoder->openHevcFrameCpy.frameInfo.nVPitch * decoder->openHevcFrameCpy.frameInfo.nHeight >> format;
    if(decoder->yuv_buffer == NULL)
    {
        decoder->yuv_buffer = (uint8_t*)malloc(sizeof(uint8_t) *(y_len + u_len + v_len));
    }
//    cv::Size actual_size(openHevcFrameCpy.frameInfo.nWidth, openHevcFrameCpy.frameInfo.nHeight);
//    cv::Size half_size(openHevcFrameCpy.frameInfo.nWidth>>1, openHevcFrameCpy.frameInfo.nHeight>>1);
//    cv::Mat y(actual_size, CV_8UC1,  openHevcFrameCpy.pvY);
//    cv::Mat u(half_size, CV_8UC1, openHevcFrameCpy.pvU);
//    cv::Mat v(half_size, CV_8UC1, openHevcFrameCpy.pvV);
//    cv::Mat u_resized, v_resized;
//    cv::resize(u, u_resized, actual_size, 0, 0, cv::INTER_NEAREST); //repeat u values 4 times
//    cv::resize(v, v_resized, actual_size, 0, 0, cv::INTER_NEAREST); //repeat v values 4 times
//
//    std::vector<cv::Mat> yuv_channels = { y, u_resized, v_resized};
//    cv::Mat yuv;
//    cv::Mat img;
//    cv::merge(yuv_channels, yuv);
//    cvtColor(yuv, img, COLOR_YUV2RGB_I420);
    

    memcpy(decoder->yuv_buffer, decoder->openHevcFrameCpy.pvY, y_len);
    memcpy(decoder->yuv_buffer + y_len, decoder->openHevcFrameCpy.pvU, u_len);
    memcpy(decoder->yuv_buffer + y_len + u_len, decoder->openHevcFrameCpy.pvV, v_len);
    
    
    Mat img;
    Mat raw_data = Mat(Size(decoder->openHevcFrameCpy.frameInfo.nWidth, decoder->openHevcFrameCpy.frameInfo.nHeight * 3 / 2), CV_8UC1, decoder->yuv_buffer);
    cvtColor(raw_data, img, COLOR_YUV2BGR_I420);
    Mat crop_img = img(decoder->tiles_position[tile_id]);
    decoder->frameVectorLock.lock();
    
    fObj->frame_id = frame_id;
    fObj->tile_id = tile_id;
    fObj->rawImage = crop_img;
    
    now = getNowTime();
    //char logContent[256];
    sprintf(logContent, "tile_convert frame: %d tile: %d time: %lld\n", frame_id, tile_id, now);
    fwrite(logContent, sizeof(char), strlen(logContent), decoder->logHandler);
    fflush(decoder->logHandler);
    decoder->decodedFrames.push(fObj);
    decoder->frameVectorSemaphore->Signal();
    decoder->frameVectorLock.unlock();
    //printf("output frame %d, %d", frame_id, tile_id);
//    char filename[256];
//    sprintf(filename, "%s_frame_%d_tile_%d.jpg", decoder->fileName.data(), frame_id, tile_id);
//    imwrite(filename, img);
}

void* OpenHEVCDecoder::run(void* context)
{
    OpenHEVCDecoder* decoder = (OpenHEVCDecoder*)context;
    decoder->status = DECODER_RUN;
    decoder->openHevcFrameCpy.pvU = NULL;
    decoder->openHevcFrameCpy.pvY = NULL;
    decoder->openHevcFrameCpy.pvV = NULL;
    decoder->yuv_buffer = NULL;
    //
    
    int video_property_len = 5;
    int* video_property = (int*) malloc(sizeof(int) * video_property_len); 
    int n = read_sock(decoder->new_socket, video_property, sizeof(int32_t) * video_property_len);
    printf("video property read %d bytes\n", n);
    decoder->videoProperty.tile_width = video_property[0];
    decoder->videoProperty.tile_height = video_property[1];
    decoder->videoProperty.video_width = video_property[2];
    decoder->videoProperty.video_height = video_property[3];
    decoder->tile_count = video_property[0] * video_property[1];
    int file_name_len = video_property[4];
    
    char filename[256];
    memset(filename, 0, 256);
    read_sock(decoder->new_socket, filename, file_name_len);
    fprintf(stdout, "video_name: %s\n", filename);
    const char* logFileName = "data/log/decoder.log";
    decoder->logHandler = fopen(logFileName, "w+");

    //decoder->fileName = String(filename);
    decoder->videoProperty.video_name = String(filename);
    decoder->videoPropertySemaphore->Signal();
    decoder->calculate_tiles_position();
    decoder->handlers = (OpenHevc_Handle*)malloc(sizeof(OpenHevc_Handle) * decoder->tile_count);
    std::vector<std::queue<int>> frame_id_list;
    for(int i = 0; i < decoder->tile_count; i ++)
    {
        std::queue<int> tile_queue;
        frame_id_list.push_back(tile_queue);
    }
    //int *frame_id_list =(int*) malloc(sizeof(int) * decoder->tile_count);
    //memset(frame_id_list, 0, sizeof(int) * decoder->tile_count);
    for(int i = 0; i < decoder->tile_count; i ++)
    {
        int nb_pthreads = 1;
        int thread_type = 1;
        decoder->handlers[i] = libOpenHevcInit(nb_pthreads, thread_type/*, pFormatCtx*/);
        if (!decoder->handlers[i]) {
            fprintf(stderr, "could not open OpenHevc\n");
            exit(1);
        }
        libOpenHevcStartDecoder(decoder->handlers[i]);
        libOpenHevcSetTemporalLayer_id(decoder->handlers[i], 7);
        libOpenHevcSetActiveDecoders(decoder->handlers[i], 0);
        libOpenHevcSetViewLayers(decoder->handlers[i], 0);
        
    }
    int got_picture = 0;
   
    while(decoder->status == DECODER_RUN){
        int32_t property[3];
        int read_len = read_sock(decoder->new_socket, property, sizeof(int32_t) * 3);
        if(read_len>0)
        {
            int frame_id = property[0];
            int tile_id = property[1];
            int buffer_len = property[2];
            if (frame_id == -1 && tile_id == -1 && buffer_len == -1)
            {
                for(int i = 0; i < decoder->tile_count; i ++){
                    libOpenHevcClose(decoder->handlers[i]);
                }
                output_file(decoder, -1, -1);
                break;
            } 
            if(tile_id >= 0)
            { 
                frame_id_list[tile_id].push(frame_id);
            }

            long long now = getNowTime();
            char logContent[256];
            if (tile_id >= 0)
            {
                sprintf(logContent, "tile_recv_start frame: %d tile: %d size: %d time: %lld\n", frame_id, tile_id, buffer_len, now);
                fwrite(logContent, sizeof(char), strlen(logContent), decoder->logHandler);
                fflush(decoder->logHandler);
            }
            
            uint8_t* buffer = (uint8_t*) malloc(sizeof(uint8_t) * buffer_len);
            int n = 0;

            while(n<buffer_len)
            {
                n += read_sock(decoder->new_socket, buffer + n, buffer_len - n);
            }
            
            if (tile_id < 0)
            {
                for(int i = 0; i < decoder->tile_count; i ++)
                {
                    if (libOpenHevcDecode(decoder->handlers[i], buffer, buffer_len, AV_NOPTS_VALUE) > 0)
                    {
                        output_file(decoder, frame_id_list[i].front(), i);
                        frame_id_list[i].pop();
                    }
                }
            }
            else
            {
                now = getNowTime();
                sprintf(logContent, "tile_recv_end frame: %d tile: %d size: %d time: %lld\n", frame_id, tile_id, buffer_len, now);
                fwrite(logContent, sizeof(char), strlen(logContent), decoder->logHandler);
                fflush(decoder->logHandler);
                if (libOpenHevcDecode(decoder->handlers[tile_id], buffer, buffer_len, AV_NOPTS_VALUE) > 0)
                {
                    output_file(decoder, frame_id_list[tile_id].front(), tile_id);
                    frame_id_list[tile_id].pop();
                }
            }
            
        }
        else{
            int all_decoder_got = 0;
            for(int i = 0; i < decoder->tile_count; i ++)
            {
                got_picture = libOpenHevcDecode(decoder->handlers[i], NULL,  0, AV_NOPTS_VALUE);
                if (got_picture > 0){
                    output_file(decoder, frame_id_list[i].front(), i);
                    frame_id_list[i].pop();
                }
                all_decoder_got += got_picture;
            }
            if(all_decoder_got == 0)
            {
                decoder->status = DECODER_EXIT;
                fprintf(stdout, "exit");
            }
        }
    }    
    return NULL;
}

void OpenHEVCDecoder::calculate_tiles_position()
{
    int vw = this->videoProperty.video_width;
    int vh = this->videoProperty.video_height;
    int tw = this->videoProperty.tile_width;
    int th = this->videoProperty.tile_height;
    printf("video property: w: %d, h: %d, tw: %d, th: %d\n", vw, vh, tw, th);
    int width_lcu_count = CEILDIV(vw, 64);
    int height_lcu_count = CEILDIV(vh, 64);
    printf("%d\n", height_lcu_count);
    int* tiles_width = (int*) malloc(sizeof(int) * tw);
    int* tiles_height = (int*)malloc(sizeof(int) * th);
    for(int i = 0; i < tw; i ++)
    {
        tiles_width[i] = (i + 1) * width_lcu_count / tw - i * width_lcu_count / tw;
    }
    for(int i = 0; i < th; i ++)
    {
        tiles_height[i] = (i + 1) * height_lcu_count / th - i * height_lcu_count / th;
        printf("height: %d\n", tiles_height[i]);
    }
    int* tiles_x_pos = (int*)malloc(sizeof(int) * tw);
    int* tiles_y_pos = (int*)malloc(sizeof(int) * th);
    for(int i = 0; i < tw; i ++)
    {
        if(i == 0)
        {
            tiles_x_pos[i] = 0;
        }
        else
        {
            tiles_x_pos[i] = tiles_x_pos[i - 1] + tiles_width[i - 1];
        }
    }
    for(int i = 0; i < th; i ++)
    {
        if(i == 0)
        {
            tiles_y_pos[i] = 0;
        }
        else
        {
            tiles_y_pos[i] = tiles_y_pos[i - 1] + tiles_height[i - 1];
        }
    }
    for(int i = 0; i< tw; i ++)
    {
        tiles_x_pos[i] = tiles_x_pos[i] * 64;
    }

    for(int i = 0; i < th; i ++)
    {
        tiles_y_pos[i] = tiles_y_pos[i] * 64;
    }
    for(int j = 0; j < th; j ++)
    {
        for(int i = 0; i < tw; i ++)
        {
            Rect x(tiles_x_pos[i], tiles_y_pos[j], min(tiles_width[i] * 64, vw - tiles_x_pos[i]), min(tiles_height[j] * 64, vh - tiles_y_pos[j]));
            printf("%d tile: x: %d, y: %d, w: %d, h: %d\n", i * th + j, x.x, x.y, x.width, x.height);
            this->tiles_position.push_back(x);
        }
    }
}




