//
// Created by Xu Wang on 2019/12/15.
//
#include <filesystem>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <opencv2/imgcodecs.hpp>
#include <fstream>
#include <arpa/inet.h>
#include <sys/types.h>
#include <unistd.h>
#include "EdgeEncoder.hpp"
#include "../EdgeApp.hpp"
#include "../utils/Utils.hpp"

using namespace Edge;
using namespace std::__fs::filesystem;
using namespace cv::kvazaar_encoder;

EdgeEncoder::EdgeEncoder(EdgeApp *app) : EdgeComponent(app, "encoder") {
    encoder = nullptr;
    videoAttrs = nullptr;
    dataQueue.queue_name = "readyEncodingFrames";
    string tile_split = config["tile_split"].Scalar();
    stringstream ss(tile_split);
    ss >> tile_width;
    if (ss.peek() == 'x')
        ss.ignore();
    ss >> tile_height;

    currentPolicy = EdgeGroupPolicy(this);
    auto group_policy = config["group_policy"].Scalar();
    if (group_policy == "1s") {
        EdgeGroupPolicy::one_group_policy(tile_width, tile_height, currentPolicy);
    } else {
        EdgeGroupPolicy::default_policy(tile_width, tile_height, currentPolicy);
    }
}


void EdgeEncoder::HEVCEncode(string video_name) {
    string exp_dir = this->app->get_file_path(app->config["exp_dir"].Scalar());
    encoder = new KvazaarEncoder(video_name, exp_dir);
    edge_logger->logger->info(fmt::format("encoder video: {0}", video_name));
    if (this->config["mode"].Scalar() == "SERVER_MODE") {
        auto ip_addr = config["ip_addr"].Scalar();
        auto port = config["port"].Scalar();
        cv::kvazaar_encoder::KvazaarEncoder::setServerMode(ip_addr, std::stoi(port));
    } else if (this->config["mode"].Scalar() == "LOCAL_FILE_MODE") {
        cv::kvazaar_encoder::KvazaarEncoder::setFileMode();
    }
    if (!is_init()) {
        edge_logger->logger->error("encoder must be initialized first...");
        return;
    }

    int gop_size = 10;
    string tile_split = config["tile_split"].Scalar();
    int nThreads = std::stoi(config["num_thread"].Scalar());
    string quality = config["quality"].Scalar();
    string roi_path = this->app->get_file_path(app->config["roi_path"].Scalar());
    string upload_order_path = this->app->get_file_path(app->config["upload_order_path"].Scalar());
    encoder->start(videoAttrs->width, videoAttrs->height, gop_size,
                   tile_split,
                   nThreads, quality, roi_path, upload_order_path);
    cv::String priority = currentPolicy.toString();
    encoder->setEncodingPriority(priority);
    while (!is_stopped()) {
        //get frames
        shared_ptr<EdgeFrame> frame = dataQueue.get();

        if (frame->frame_idx == -1) {
            encoder->stop();
            //client->feed_cache_frame(frame);
            while (encoder->getEncodeStatus() != -1) {
                usleep(10000);
            }
            break;
        } else {
            frame->convert_rgb2yuv();
            auto group_policy = config["group_policy"].Scalar();
            if (group_policy == "4d") {
                currentPolicy = currentPolicy.dynamic_by_count();
                cv::String new_priority = currentPolicy.toString();
                encoder->setEncodingPriority(new_priority);
            }
            EncoderResult encoder_status{};
            while (1) {
                encoder_status = encoder->encode(frame->yuv_frame[0], frame->yuv_frame[1],
                                                 frame->yuv_frame[2], frame->frame_idx);
                if (encoder_status.encoderState == 1) {
                    break;
                }
            }
            if (encoder_status.encoderState == 1) {
                frame->will_upload = true;
                frame->groupPolicy = currentPolicy;
            }

            //释放空间
            for (int i = 0; i < 3; i++) {
                frame->yuv_frame[i].release();
            }
            frame->yuv_data.release();
        }
    }

    edge_logger->logger->info("encoder thread exit...");
}

void EdgeEncoder::FakeEncode(string video_name) {

    edge_logger->logger->info("running fake encoder");
    auto video_path = path(videoAttrs->file_path);
    //encoder->setEncodingPriority(priority);

    while (!is_stopped()) {
        //get frames
        shared_ptr<EdgeFrame> frame = dataQueue.get();
        if (frame->frame_idx == -1) {
            int32_t header[5];
            header[0] = -1;
            header[1] = -1;
            header[2] = -1;
            header[3] = -1;
            header[4] = -1;
            send(sock, header, sizeof(int32_t) * 5, 0);
            shutdown(sock, SHUT_RDWR);
            break;
        } else {
            if (hevc_data.find(frame->frame_idx) == hevc_data.end()) {
                edge_logger->logger->error("cannot find frame in hevc file");
            }
            //frame->convert_rgb2yuv();
            //load encoding data
            auto group_policy = config["group_policy"].Scalar();
            if (group_policy == "4d") {
                currentPolicy = currentPolicy.dynamic_by_count();
                cv::String new_priority = currentPolicy.toString();
            }
            if (group_policy != "1s") {
                currentPolicy = currentPolicy.dynamic_by_object_nums(frame->frame_idx, upload_order_data[frame->frame_idx]);
            }
            
            frame->will_upload = true;
            frame->groupPolicy = currentPolicy;
            vector<TileMeta> orders = frame->groupPolicy.getTileEncodingOrder(tile_width, tile_height);
            if (frame->frame_idx == 0) {
                int video_params[5];
                video_params[0] = tile_width;
                video_params[1] = tile_height;
                video_params[2] = videoAttrs->width;
                video_params[3] = videoAttrs->height;
                video_params[4] = (int) video_path.filename().string().size();
                send(sock, video_params, sizeof(int) * 5, 0);
                send(sock, video_path.filename().string().data(), video_params[4], 0);

                // send tile -1
                int32_t header[5];
                header[0] = frame->frame_idx;
                header[1] = -1;
                header[2] = 0;
                header[3] = 0;
                header[4] = meta_data[frame->frame_idx][-1];
                send(sock, header, sizeof(int32_t) * 5, 0);
                int send_n = 0;
                int len = header[4];
                uint8_t *data = (uint8_t *) malloc(sizeof(uint8_t) * (len + 1));
                memset(data, 0, sizeof(uint8_t) * (len + 1));
                // uint8_t *data = hevc_data[frame->frame_idx][-1];
                
                while (send_n < header[4]) {
                    long n = send(sock, data + send_n, len - send_n, 0);
                    if (n < 0) {
                        fprintf(stderr, "socket() failed: %s\n", strerror(errno));
                        break;
                    } else {
                        send_n += n;
                    }
                }

            }
            float encoder_time = 40;
            for (TileMeta &tmeta: orders) {
                usleep(encoder_time * 1000 / (tile_width * tile_height));
                int32_t header[5];
                this->edge_logger->logger->info(fmt::format("*updoad_frame {} \n", frame->frame_idx));
                header[0] = frame->frame_idx;
                header[1] = tmeta.tile_id;
                header[2] = tmeta.group_id;
                header[3] = (tmeta.group_width << 8) + tmeta.group_height;
                header[4] = meta_data[frame->frame_idx][tmeta.tile_id];
                printf("frame:%d tile:%d group:%d len:%d\n", frame->frame_idx,tmeta.tile_id,tmeta.group_id,header[4]);
                send(sock, header, sizeof(int32_t) * 5, 0);
                int send_n = 0;
                int len = header[4];
                uint8_t *data = (uint8_t *) malloc(sizeof(uint8_t) * (len + 1));
                memset(data, 0, sizeof(uint8_t) * (len + 1));
                // uint8_t *data = hevc_data[frame->frame_idx][tmeta.tile_id];
                while (send_n < header[4]) {
                    long n = send(sock, data + send_n, len - send_n, 0);
                    if (n < 0) {
                        fprintf(stderr, "socket() failed: %s\n", strerror(errno));
                        break;
                    } else {
                        send_n += n;
                    }
                }

                // wait for

            }
        }
    }

    edge_logger->logger->info("encoder thread exit...");
}

void EdgeEncoder::JPEGEncode(string video_name) {
    while (!is_stopped()) {
        //get frames
        shared_ptr<EdgeFrame> frame = dataQueue.get();

        if (frame->frame_idx == -1) {
            break;
        } else {
            // encode yuv to jpeg. -- by jiahang
            long long bf = Utils::current_time();

            // convert color from yuv to rgb
            cv::Mat rgb_data;
            cvtColor(frame->yuv_data, rgb_data, cv::COLOR_YUV2BGR_I420);

            // set jpeg quality
            int m_jpegQuality = std::stoi(this->config["jpeg_quality"].Scalar());
            vector<int> compression_params;
            compression_params.push_back(cv::IMWRITE_JPEG_QUALITY);
            compression_params.push_back(m_jpegQuality);

            // create the folder to save the compressed jpeg picture
            string img_folder;

            img_folder = this->app->get_file_path(config["jpeg_folder"].Scalar()).string();

            if (0 != access(img_folder.c_str(), 0)) {
                fprintf(stdout, "Folder [%s] not exist. Create new one.\n", img_folder.c_str());
                int r = mkdir(img_folder.c_str(), S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
                if (r == 0) {
                    fprintf(stdout, "Create folder [%s] succeeded.\n", img_folder.c_str());
                } else {
                    fprintf(stdout, "Create folder [%s] failed.\n", img_folder.c_str());
                }
            }

            // set picture name and set path to save the jpg
            char out_file[256];
            sprintf(out_file, "%s/img%d.jpg", img_folder.c_str(), frame->frame_idx);
            // save the jpeg picture
            //cv::imwrite(out_file, rgb_data, compression_params);
            long long af = Utils::current_time();
            // get jpeg file size
            FILE *fp = fopen(out_file, "r");
            fseek(fp, 0L, SEEK_END);
            long pic_size = ftell(fp);
            fclose(fp);

            // calculate the PSRN and SSIM
//            cv::Mat ret;
//            ret = cv::imread(out_file);
//            double psnr = Utils::getPSNR(frame->raw_frame, ret);
//            cv::Scalar ssim = Utils::getMSSIM(frame->raw_frame, ret);
            this->edge_logger->logger->info(
                    fmt::format("frame:{}, time_cost:{}, img_size:{}, psnr:{:.4f}, ssim:{:.4f}\n",
                                frame->frame_idx, af - bf,
                                pic_size,
                                0.1,
                                0.1));
//            this->edge_logger->logger->info(fmt::format("frame:{}, time_cost:{}, img_size:{}, psnr:{:.4f}, ssim:{:.4f}\n",
//                                                        frame->frame_idx, af - bf,
//                                                        pic_size,
//                                                        psnr,
//                                                        (ssim.val[0]+ssim.val[1]+ssim.val[2])/3.0));
            frame->will_upload = true;
            // free yuv
            for (int i = 0; i < 3; i++) {
                frame->yuv_frame[i].release();
            }
            frame->yuv_data.release();

            //client->feed_cache_frame(frame);

        }
    }
}

void EdgeEncoder::run() {
    calculate_tiles_position();
    auto video_path_str = videoAttrs->file_path;
    edge_logger->logger->info(fmt::format("snapshot video path: {0}", video_path_str));
    auto video_path = path(video_path_str);
    auto video_name = video_path.filename().string();
    string encode_type = this->config["encode_type"].Scalar();
    if (encode_type == "JPEG") {
        JPEGEncode(video_name);
    } else if (encode_type == "FAKE") {
        FakeEncode(video_name);
    } else {
        HEVCEncode(video_name);
    }
}


void EdgeEncoder::initialize() {
    auto video_path = path(
            this->app->get_file_path(app->config["video_path"].Scalar()));
    auto video_name = video_path.filename().string();
    string encode_type = this->config["encode_type"].Scalar();

    if (encode_type == "FAKE") {
        //auto video_path = path(client->get_framePool()->video_path);
        string tile_split = config["tile_split"].Scalar();
        string hevc_file = video_path.parent_path()/ video_path.stem().string() / tile_split /  (video_path.stem().string() + ".hevc");
        string meta_file = video_path.parent_path() /video_path.stem().string() / tile_split /  (video_path.stem().string() + ".meta");
        printf("meta file:%s\n",meta_file.c_str());
        string upload_order_file = path(
            this->app->get_file_path(app->config["upload_order_path"].Scalar()));
        // FILE *hevc_handler = fopen(hevc_file.data(), "rb");
        ifstream upload_order_handler(upload_order_file.data());
        ifstream meta_handler(meta_file.data());
        string exp_dir = this->app->get_file_path(app->config["exp_dir"].Scalar());

        edge_logger->logger->info(fmt::format("encoder video: {0}", video_name));

        auto ip_addr = config["ip_addr"].Scalar();
        auto port = config["port"].Scalar();

        struct sockaddr_in server_addr{};
        if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
            fprintf(stderr, "Socket creation error \n");
        }

        server_addr.sin_family = AF_INET;
        int port_num = std::stoi(port);
        server_addr.sin_port = htons(port_num);

        // Convert IPv4 and IPv6 addresses from text to binary form
        if (inet_pton(AF_INET, ip_addr.data(), &server_addr.sin_addr) <= 0) {
            fprintf(stderr, "Address not supported \n");
        }


        if (connect(sock, (struct sockaddr *) &server_addr, sizeof(server_addr)) < 0) {
            fprintf(stderr, "Connection Failed \n");
        }
        fprintf(stdout, "connect to server\n");

        //string tile_split = config["tile_split"].Scalar();
        cv::String priority = currentPolicy.toString();

        std::string line;

        while (std::getline(meta_handler, line)) {
            int frame_id, tile_id, data_len;
            char tmp;
            std::istringstream iss(line);
            if (!(iss >> frame_id >> tmp >> tile_id >> tmp >> data_len)) { break; } // error
            if (hevc_data.find(frame_id) == hevc_data.end()) {
                hevc_data[frame_id] = map<int, uint8_t *>();
            }
            if (meta_data.find(frame_id) == meta_data.end()) {
                meta_data[frame_id] = map<int, int>();
            }
            meta_data[frame_id][tile_id] = data_len;
            // uint8_t *buf = (uint8_t *) malloc(sizeof(uint8_t) * (data_len + 1));
            // fread(buf, sizeof(uint8_t), data_len, hevc_handler);
            // hevc_data[frame_id][tile_id] = buf;
            // activate network status
        }

        while (std::getline(upload_order_handler, line)){
            int frame_id;
            
            std::istringstream iss(line);
            char tmp;
            if (!(iss >> frame_id >> tmp)) { break; } // error
            if (upload_order_data.find(frame_id) == upload_order_data.end()) {
                upload_order_data[frame_id] = vector<int>();
            }
            for(int i = 0; i < tile_width*tile_height; i++){
                int tile_id;
                iss >> tile_id;
                upload_order_data[frame_id].push_back(tile_id);
            }
        }
    }
}

void EdgeEncoder::calculate_tiles_position() {
    int vw = videoAttrs->width;
    int vh = videoAttrs->height;
    int tw = tile_width;
    int th = tile_height;

    printf("video property: w: %d, h: %d, tw: %d, th: %d\n", vw, vh, tw, th);
    int width_lcu_count = CEILDIV(vw, 64);
    int height_lcu_count = CEILDIV(vh, 64);
    printf("%d\n", height_lcu_count);
    int *tiles_width = (int *) malloc(sizeof(int) * tw);
    int *tiles_height = (int *) malloc(sizeof(int) * th);
    for (int i = 0; i < tw; i++) {
        tiles_width[i] = (i + 1) * width_lcu_count / tw - i * width_lcu_count / tw;
    }
    for (int i = 0; i < th; i++) {
        tiles_height[i] = (i + 1) * height_lcu_count / th - i * height_lcu_count / th;
        printf("height: %d\n", tiles_height[i]);
    }
    int *tiles_x_pos = (int *) malloc(sizeof(int) * tw);
    int *tiles_y_pos = (int *) malloc(sizeof(int) * th);
    for (int i = 0; i < tw; i++) {
        if (i == 0) {
            tiles_x_pos[i] = 0;
        } else {
            tiles_x_pos[i] = tiles_x_pos[i - 1] + tiles_width[i - 1];
        }
    }
    for (int i = 0; i < th; i++) {
        if (i == 0) {
            tiles_y_pos[i] = 0;
        } else {
            tiles_y_pos[i] = tiles_y_pos[i - 1] + tiles_height[i - 1];
        }
    }
    for (int i = 0; i < tw; i++) {
        tiles_x_pos[i] = tiles_x_pos[i] * 64;
    }

    for (int i = 0; i < th; i++) {
        tiles_y_pos[i] = tiles_y_pos[i] * 64;
    }
    for (int j = 0; j < th; j++) {
        for (int i = 0; i < tw; i++) {
            Rect x(tiles_x_pos[i], tiles_y_pos[j], min(tiles_width[i] * 64, vw - tiles_x_pos[i]),
                   min(tiles_height[j] * 64, vh - tiles_y_pos[j]));
            printf("%d tile: x: %d, y: %d, w: %d, h: %d\n", i * th + j, x.x, x.y, x.width, x.height);
            this->tiles_position.push_back(x);
        }
    }

}

float EdgeEncoder::getFrameEncodingTile() {
    return encoder->getFrameEncodingTime();
}