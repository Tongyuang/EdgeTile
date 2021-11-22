//
// Created by Xu Wang on 2019/12/15.
//

#include "include/EdgeClient.hpp"
#include "components/EdgeEncoder.hpp"

#include "components/EdgeTracker.hpp"
#include "components/EdgeSocket.hpp"
#include "datatype/EdgeVideo.hpp"
#include "utils/Utils.hpp"

#if defined(__APPLE__)

#include "TargetConditionals.h"

#endif

using namespace Edge;


EdgeClient::EdgeClient(string root_path, YAML::Node config) : EdgeApp("client", "EdgeTileClient", root_path, config) {
    this->edge_logger->logger->info("start running EdgeClient");
    this->framePool = shared_ptr<EdgeFramePool>(new EdgeFramePool(this));
}

void EdgeClient::start() {
    this->register_component("video_streamer", "EdgeStreamer");
    //this->register_component("control", "EdgeController");
    this->register_component("encoder", "EdgeEncoder");
    this->register_component("socket", "EdgeSocket");
    this->register_component("tracker", "EdgeTracker");
    this->initialize();
    this->start_components();

}


void EdgeClient::stop() {

}

void EdgeClient::feed_encode_frame(std::shared_ptr<EdgeFrame> frame) {
    int skip = stoi(this->config["encoder_skip"].Scalar());
    if ((frame->frame_idx % skip == 0) || frame->frame_idx < 0) {
        EdgeEncoder *encoder = (EdgeEncoder *) get_components_by_name("encoder");
        //record all frames in snapshot
        frame->before_encoding_time = Utils::current_time();
        encoder->dataQueue.put(frame);
    }
}

void EdgeClient::feed_tracker_frame(std::shared_ptr<EdgeFrame> frame) {
    frame->before_tracking_time = Utils::current_time();
    int fps = stoi(this->config["fps"].Scalar());
    printf("fps:%d\n", fps);
    if ((frame->frame_idx % (120/fps) == 0) || frame->frame_idx < 0) {
        EdgeTracker *tracker = (EdgeTracker *) get_components_by_name("tracker");
        tracker->dataQueue.put(frame);
        //this->readyTrackFrames.put(frame);
    }
}

void EdgeClient::feed_render_frame(shared_ptr<EdgeFrame> frame) {
    frame->before_render_time = Utils::current_time();
    if (frame->frame_idx % 10 == 0) {
        edge_logger->logger->info("app is running in {} fps", get_framePool()->calculate_fps(frame->frame_idx));
    }
    // this->readyRenderFrames.put(frame);
}

void EdgeClient::feed_detector_frame(shared_ptr<EdgeFrame> frame) {
    int skip = stoi(this->config["detector_skip"].Scalar());
    if ((frame->frame_idx % skip == 0) || frame->frame_idx < 0) {
        this->readyDetectFrames.put(frame);
    }
}

shared_ptr<EdgeFramePool> EdgeClient::get_framePool() {
    //EdgeController *control = (EdgeController *) get_components_by_name("control");
    return framePool;
}

void EdgeClient::shutdown_socket() {
    EdgeSocket *socket = (EdgeSocket *) get_components_by_name("socket");
    socket->shutdown();
}

void EdgeClient::evaluate(float iou_thres) {
    auto snap = get_framePool();
    map<string, float> detect_count;
    map<string, float> pred_count;
    map<string, float> gt_count;
    vector<float> iou_array;
    for (auto f : snap->frames) {
        if (f->is_track_finished) {
            cv::Mat iou_matrix(f->gt_bboxes.size(), f->client_bboxes.size(), CV_32F, Scalar(0.0));

            for (int i = 0; i < f->gt_bboxes.size(); i++) {
                auto gt_b = f->gt_bboxes[i];
                if (gt_count.find(gt_b.class_name) == gt_count.end()) {
                    gt_count[gt_b.class_name] = 0;
                }
                gt_count[gt_b.class_name] += 1;
                for (int j = 0; j < f->client_bboxes.size(); j++) {
                    auto pred_b = f->client_bboxes[j];
                    if (gt_b.class_name == pred_b.class_name) {
                        double iou = gt_b.calculate_iou(pred_b);
                        iou_matrix.at<float>(i, j) = iou;
                    }
                }
            }

            for (auto pred_b: f->client_bboxes) {
                if (pred_count.find(pred_b.class_name) == pred_count.end()) {
                    pred_count[pred_b.class_name] = 0;
                }
                pred_count[pred_b.class_name] += 1;
            }

            // match

            for (int i = 0; i < f->gt_bboxes.size(); i++) {
                auto v = iou_matrix.row(i);
                double min = 0, max = 0;
                Point minLoc, maxLoc;
                minMaxLoc(v, &min, &max, &minLoc, &maxLoc);

                iou_array.push_back(max);
                if (max > iou_thres) {
                    if (detect_count.find(f->client_bboxes[maxLoc.x].class_name) == detect_count.end()) {
                        detect_count[f->client_bboxes[maxLoc.x].class_name] = 0;
                    }
                    detect_count[f->client_bboxes[maxLoc.x].class_name] += 1;
                    iou_matrix.col(maxLoc.x).setTo(Scalar(0.0));
                    //printf("%d, %f\n", maxLoc.x, max);
                }


            }
            //printf("\n");
        }
    }
    // calculate precision, recall and f1
    vector<string> class_names;
    class_names.push_back("pedestrian");
    class_names.push_back("car");
    float total_detect = 0;
    float total_pred = 0;
    float total_gt = 0;
    vector<float> test_datas;
    edge_logger->logger->info("cat\tprec\trec\tf1");
    for (auto c: class_names) {
        total_detect += detect_count[c];
        total_pred += pred_count[c];
        total_gt += gt_count[c];
        float p = detect_count[c] / pred_count[c];
        float r = detect_count[c] / gt_count[c];
        float f1 = 2 * p * r / (p + r);
        edge_logger->logger->info("{0}\t{1:.4f}\t{2:.4f}\t{3:.4f}", c, p, r, f1);
        test_datas.push_back(p);
        test_datas.push_back(r);
        test_datas.push_back(f1);
    }
    float p2 = total_detect / total_pred;
    float r2 = total_detect / total_gt;
    float f12 = 2 * p2 * r2 / (p2 + r2);
    test_datas.push_back(p2);
    test_datas.push_back(r2);
    test_datas.push_back(f12);
    double iou_sum = 0;
    for (int i = 0; i < iou_array.size(); i++) {
        iou_sum += iou_array[i];
    }
    float iou_accu = iou_sum * 1.0 / iou_array.size();
    edge_logger->logger->info("{0}\t{1:.4f}\t{2:.4f}\t{3:.4f}", "total", p2, r2,
                              f12, iou_accu);
    edge_logger->logger->info("iou_accu:{0:.4f}", iou_accu);
    string result_str = "";
    for (int i = 0; i < test_datas.size(); i++) {
        char word[8];
        sprintf(word, "%.3f", test_datas[i]);
        string word_str = word;
        result_str = result_str + word_str;
        if (i != test_datas.size() - 1) result_str = result_str + ",";
    }
    edge_logger->logger->info("result:{0}", result_str);

}

float EdgeClient::getFrameEncodingTime() {
    EdgeEncoder *encoder = (EdgeEncoder *) get_components_by_name("encoder");
    return encoder->getFrameEncodingTile();
}

void EdgeClient::handle_yield(EdgeComponent *component, shared_ptr<EdgePacket> packet) {
    if (component) {
        if (component->component_name == "video_streamer") {
            if (packet->data_type == "EdgeVideo") {
                shared_ptr<EdgeVideo> attrs = std::dynamic_pointer_cast<EdgeVideo>(packet);
                framePool->videoAttrs = attrs;
                EdgeEncoder *encoder = (EdgeEncoder *) get_components_by_name("encoder");
                encoder->videoAttrs = attrs;
                EdgeTracker *tracker = (EdgeTracker *) get_components_by_name("tracker");
                tracker->framePool = framePool;
            } else if (packet->data_type == "EdgeFrame") {
                shared_ptr<EdgeFrame> frame = std::dynamic_pointer_cast<EdgeFrame>(packet);
                framePool->frames.push_back(frame);
                string detect_mode = config["detector_mode"].Scalar();
                if (detect_mode == "server") {
                    feed_encode_frame(frame);
                } else if (detect_mode == "local") {
                    feed_detector_frame(frame);
                } else if (detect_mode == "both") {
                    feed_encode_frame(frame);
                    feed_detector_frame(frame);
                }
                feed_tracker_frame(frame);
            }
        } else if (component->component_name == "socket") {
            if (packet->data_type == "EdgeBoxArray") {
                shared_ptr<EdgeBoxArray> boxArray = std::dynamic_pointer_cast<EdgeBoxArray>(packet);
                boxArray->is_server = true;
                EdgeTracker *tracker = (EdgeTracker *) get_components_by_name("tracker");
                shared_ptr<EdgeBoxArray> filteredBoxArray = shared_ptr<EdgeBoxArray>(new EdgeBoxArray());
                filteredBoxArray->frame_id = boxArray->frame_id;
                filteredBoxArray->group_id = boxArray->group_id;
                filteredBoxArray->level = boxArray->level;
                filteredBoxArray->is_server = boxArray->is_server;
                for (auto box: boxArray->boxes) {
                    float xmin = box.xmin;
                    float xmax = box.xmax;
                    float ymin = box.ymin;
                    float ymax = box.ymax;
                    float box_size = (xmax - xmin) * (ymax - ymin);
                    filteredBoxArray->boxes.push_back(box);
                }
                tracker->update_reference_bbox(filteredBoxArray); // 向readyboxarray里面append
            }
        } else if (component->component_name == "tracker") {
            if (packet->data_type == "EdgeFrame") {
                shared_ptr<EdgeFrame> frame = std::dynamic_pointer_cast<EdgeFrame>(packet);
                feed_render_frame(frame);
            }
        }
    } else {
        if (packet->data_type == "EdgeBoxArray") {
            
            shared_ptr<EdgeBoxArray> boxArray = std::dynamic_pointer_cast<EdgeBoxArray>(packet);
            this->get_framePool()->local_finish_frame_timestamps[boxArray->frame_id].first = Utils::current_time();
            this->get_framePool()->local_finish_frame_timestamps[boxArray->frame_id].second = boxArray->boxes;
            for (int i = 0; i < boxArray->boxes.size(); i++) {
                this->get_framePool()->local_detect_boxes[boxArray->frame_id].push_back(boxArray->boxes[i]);
            }
            string detect_mode = config["detector_mode"].Scalar();
            if(detect_mode == "local"){
                int frame_id = boxArray->frame_id;
                int group_id = boxArray->group_id;
                if(this->get_framePool()->valid_local_finish_frame_timestamps.find(frame_id) == this->get_framePool()->valid_local_finish_frame_timestamps.end()){
                    this->get_framePool()->valid_local_finish_frame_timestamps[frame_id] = map<int, pair<long long, vector<EdgeBox>>>();
                }
                this->get_framePool()->valid_local_finish_frame_timestamps[frame_id][group_id].first = this->get_framePool()->local_finish_frame_timestamps[frame_id].first;
                this->get_framePool()->valid_local_finish_frame_timestamps[frame_id][group_id].second = boxArray->boxes;
            }
            
            boxArray->is_server = false;

            shared_ptr<EdgeBoxArray> filteredBoxArray = shared_ptr<EdgeBoxArray>(new EdgeBoxArray());
            filteredBoxArray->frame_id = boxArray->frame_id;
            filteredBoxArray->group_id = boxArray->group_id;
            filteredBoxArray->level = boxArray->level;
            filteredBoxArray->is_server = boxArray->is_server;
            for (auto box: boxArray->boxes) {
                float xmin = box.xmin;
                float xmax = box.xmax;
                float ymin = box.ymin;
                float ymax = box.ymax;
                float box_size = (xmax - xmin) * (ymax - ymin);
                filteredBoxArray->boxes.push_back(box);
            }
            


            EdgeTracker *tracker = (EdgeTracker *) get_components_by_name("tracker");
            tracker->update_reference_bbox(filteredBoxArray);
        }
    }
}
