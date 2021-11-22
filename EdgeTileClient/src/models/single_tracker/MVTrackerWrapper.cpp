//
// Created by 吴家行 on 2020/8/5.
//

#include "MVTrackerWrapper.hpp"

MVTrackerWrapper::MVTrackerWrapper() {
}

EdgeBox MVTrackerWrapper::update(shared_ptr<EdgeFrame> frame) {
    EdgeBox b;
    vector<int> dxs;
    vector<int> dys;

    // motion vector tracker update
    // 1. get all the motion vector that reside in the last offloaded
    // bounding box in the current frame
    for (auto vec: frame->motion_vectors) {
        int src_x = vec["src_x"];
        int src_y = vec["src_y"];
        int dst_x = vec["dst_x"];
        int dst_y = vec["dst_y"];
        if (src_x >= b.xmin && src_x <= b.xmax &&
            src_y >= b.ymin && src_y >= b.ymax &&
            dst_x >= b.xmin && dst_x <= b.xmax &&
            dst_y >= b.ymin && dst_y >= b.ymax){
            dxs.push_back(dst_x-src_x);
            dys.push_back(dst_y-src_y);
        }
    }

    // 2. calculate the mean of all motion vectors that reside in the bounding box.
    long long sum_dx = 0;
    long long sum_dy = 0;
    for(int i = 0; i < dxs.size(); i++){
        int dx = dxs[i];
        int dy = dys[i];
        sum_dx += dx;
        sum_dy += dy;
    }
    double mean_dx = sum_dx * 1.0 / dxs.size();
    double mean_dy = sum_dy * 1.0 / dys.size();

    // 3. shift the old bounding box to the current position
    currentRect.x = currentRect.x + mean_dx;
    currentRect.y = currentRect.y + mean_dy;

    b.xmin = currentRect.x;
    b.ymin = currentRect.y;
    b.xmax = currentRect.x + currentRect.width;
    b.ymax = currentRect.y + currentRect.height;
    b.class_name = recent_detect_box.class_name;
    b.is_server = recent_detect_box.is_server;
    return b;
}

void MVTrackerWrapper::init(EdgeBox box, shared_ptr<EdgeFrame> frame) {
    recent_detect_box = box;
    recent_detect_frame = frame->frame_idx;
    currentRect.x = box.xmin * 1.0;
    currentRect.y = box.ymin * 1.0;
    currentRect.width = (box.xmax - box.xmin) * 1.0;
    currentRect.height = (box.ymax - box.ymin) * 1.0;
}

void MVTrackerWrapper::reset(EdgeBox box, shared_ptr<EdgeFrame> frame) {
    recent_detect_box = box;
    recent_detect_frame = frame->frame_idx;
    currentRect.x = box.xmin * 1.0;
    currentRect.y = box.ymin * 1.0;
    currentRect.width = (box.xmax - box.xmin) * 1.0;
    currentRect.height = (box.ymax - box.ymin) * 1.0;
}