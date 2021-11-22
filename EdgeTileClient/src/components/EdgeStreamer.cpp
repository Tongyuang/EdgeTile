//
// Created by Xu Wang on 2019/12/16.
//
#include <filesystem>
#include "EdgeStreamer.hpp"
#include "../EdgeApp.hpp"
#include "../utils/Utils.hpp"
#include "../include/EdgeClient.hpp"


using namespace Edge;
using namespace std::__fs::filesystem;


EdgeStreamer::EdgeStreamer(Edge::EdgeApp *app) : EdgeComponent(app, "video_streamer") {
    cap = nullptr;
    readFrames = 0;
    status = STREAMER_NO_PLAY;
}

void EdgeStreamer::initialize() {
    videoAttrs.file_path = this->app->get_file_path(app->config["video_path"].Scalar());
    cap = new cv::VideoCapture(videoAttrs.file_path);
    videoAttrs.width = (int) cap->get(cv::CAP_PROP_FRAME_WIDTH);
    videoAttrs.height = (int) cap->get(cv::CAP_PROP_FRAME_HEIGHT);
    videoAttrs.fps = (int) cap->get(cv::CAP_PROP_FPS);

    // output video properties to apps
    shared_ptr<EdgeVideo> attrs = shared_ptr<EdgeVideo>(new EdgeVideo(videoAttrs));
    yield(attrs);
    edge_logger->logger->info(
            fmt::format("properties of video {0}: width({1}) height({2}) fps({3})", videoAttrs.file_path,
                        videoAttrs.width, videoAttrs.height, videoAttrs.fps));
}

void EdgeStreamer::run() {
    edge_logger->logger->info("video streamer starts to play...");
    status = STREAMER_IS_PLAY;
    int fps = 120;
    auto frame_interval = 1000.0 / fps;
    while (!is_stopped()) {
        auto start_time = Utils::current_time();
        if (next_frame()) {
            auto end_time = Utils::current_time();
            auto pass_time = end_time - start_time;
            auto remain = frame_interval - pass_time;
            edge_logger->logger->info(fmt::format("next frame for {} milliseconds", pass_time));

            if (remain > 0) {
                usleep(remain * 1000);
            }
            if (readFrames % 10 == 0) {
                edge_logger->logger->info(fmt::format("have read {} frames", readFrames));
            }
        } else {
            status = STREAMER_NO_PLAY;
            break;
        }
    }
    edge_logger->logger->info(fmt::format("Streamer thread exit..."));
}

bool EdgeStreamer::next_frame() {
    Mat m;
    bool cap_status;
    cap_status = cap->read(m);
    std::shared_ptr<EdgeFrame> f(new EdgeFrame());
    if (cap_status) {
        f->raw_frame = m;
        f->w = videoAttrs.width;
        f->h = videoAttrs.height;
        f->video_path = videoAttrs.file_path;
        f->frame_idx = readFrames;
        // 记录读帧的时间
        EdgeClient* client = (EdgeClient*)(this->app);
        client->get_framePool()->read_frame_timestamps[f->frame_idx] = Utils::current_time();

        auto anno_path = app->get_file_path(config["anno"].Scalar());
        auto frame_anno_path = anno_path / path(f->video_path).stem() / fmt::format("{:06d}.xml", f->frame_idx);
        f->load_bboxes(frame_anno_path.string(), frame_anno_path.string());
        // auto mv_path = app->get_file_path(config["mv"].Scalar());
        // auto frame_mv_path = mv_path / path(f->video_path).stem() / fmt::format("{:d}.json", f->frame_idx + 1);
        // f->load_motionVectors(frame_mv_path.string());

        auto local_detect_path = app->get_file_path(config["local_detect_path"].Scalar());
        auto frame_local_detect_path = local_detect_path / path(f->video_path).stem() / fmt::format("{:06d}.xml", f->frame_idx);
        
        // f->load_local_detect_bboxes(frame_local_detect_path.string());
        readFrames += 1;
    } else {
        f->frame_idx = -1; // -1 标志着所有的进程都会被结束
    }
    yield(f); // 更新
    return cap_status;
}