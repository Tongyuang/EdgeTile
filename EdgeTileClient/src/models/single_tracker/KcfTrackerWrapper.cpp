//
// Created by Xu Wang on 2020/4/11.
//

#include "KcfTrackerWrapper.hpp"

KCFTrackerWrapper::KCFTrackerWrapper(bool hog, bool fixed_window, bool multiscale, bool lab) {
    this->hog = hog;
    this->fixed_window = fixed_window;
    this->multiscale = multiscale;
    this->lab = lab;
    tracker = shared_ptr<KCFTracker>(new KCFTracker(hog, fixed_window, multiscale, lab));
}

EdgeBox KCFTrackerWrapper::update(shared_ptr<EdgeFrame> frame){
    EdgeBox b;
    float confidence;
    Rect2f updated_box = tracker->update(frame->raw_frame, confidence);
    b.xmin = updated_box.x;
    b.ymin = updated_box.y;
    b.xmax = updated_box.x + updated_box.width;
    b.ymax = updated_box.y + updated_box.height;
    b.class_name = recent_detect_box.class_name;
    b.confidence = confidence;
    b.is_server = recent_detect_box.is_server;
    return b;
}

void KCFTrackerWrapper::init(EdgeBox box, shared_ptr<EdgeFrame> frame) {
    recent_detect_box = box;
    recent_detect_frame = frame->frame_idx;
    Rect2d rect;
    rect.x = box.xmin * 1.0;
    rect.y = box.ymin * 1.0;
    rect.width = (box.xmax - box.xmin) * 1.0;
    rect.height = (box.ymax - box.ymin) * 1.0;
    tracker->init(rect, frame->raw_frame);
}

void KCFTrackerWrapper::reset(EdgeBox box, shared_ptr<EdgeFrame> frame) {
    recent_detect_box = box;
    recent_detect_frame = frame->frame_idx;
    tracker = shared_ptr<KCFTracker>(new KCFTracker(hog, fixed_window, multiscale, lab));
    Rect2d rect;
    rect.x = box.xmin * 1.0;
    rect.y = box.ymin * 1.0;
    rect.width = (box.xmax - box.xmin) * 1.0;
    rect.height = (box.ymax - box.ymin) * 1.0;
    tracker->init(rect, frame->raw_frame);
}
