//
// Created by Xu Wang on 2020/4/11.
//

#include "BaseSingleTracker.hpp"
#include "../../components/EdgeTracker.hpp"
#include "../../utils/Utils.hpp"

BaseSingleTracker::BaseSingleTracker(){
    mismatch = 0;
    is_server = false;
    bigL = 100000;
    priority_seed = -1;
    runtime_priority = -1;
    globalL = -1;
}

float BaseSingleTracker::priority_score(int frame_id) {
    auto last_item = traj.trajectory[traj.trajectory.size() - 1];
    float pr = frame_id - get<0>(last_item);
    int category = 1;
    if(traj.trajectory.size() >= 2){
        float speed_threshold = 2;
        float speed;
        auto item1 = traj.trajectory[traj.trajectory.size() - 1];
        auto item2 = traj.trajectory[traj.trajectory.size() - 2];
        EdgeBox b1 = get<1>(item1);
        EdgeBox b2 = get<1>(item2);
        float x1 = (b1.xmin+b1.xmax) * 1.0 / 2;
        float y1 = (b1.ymin+b1.ymax) * 1.0 / 2;
        float x2 = (b2.xmin+b2.xmax) * 1.0 / 2;
        float y2 = (b2.ymin+b2.ymax) * 1.0 / 2;
        int frame_interval = get<0>(item1) - get<0>(item2);
        speed = sqrt(pow(x2-x1,2) + pow(y2-y1,2)) / frame_interval;
        if(speed > speed_threshold){
            category = 2;
        }
    }
    category = 1;
    
    
    return - pr * 1.0 / category;
//    if(priority_seed == -1){
//        priority_seed =  (int)(bigL * rand() / (RAND_MAX + 1) / pr);
//        runtime_priority = priority_seed + globalL;
//    }
//    return runtime_priority * 1.0;
}

void BaseSingleTracker::update_priority() {
    // default
    if(priority_seed == -1){
        priority_seed =  (int)bigL * rand() / (RAND_MAX + 1);
        runtime_priority = priority_seed;
    }
    // estimate category
    int category = 1;
    runtime_priority += bigL / category;
}

void BaseSingleTracker::new_tracker() {
    if(status == TRACKER_INIT) {
        // printf("init tracker...\n");
        auto x = newArgs;
        int detector_skip = x->detector_skip;
        float iou_thres = x->iou_thres;
        shared_ptr<EdgeFrame> refer_frame = x->framePool->frames[x->frame_id];
        EdgeBox box = x->box;
        globalL = x->realtimeL;
//        bool HOG = false;
//        bool FIXEDWINDOW = true;
//        bool MULTISCALE = false;
//        bool LAB = false; // 开启会变慢
//        // Create KCFTracker object
//        x->tracker = shared_ptr<KCFTrackerWrapper>(new KCFTrackerWrapper(HOG, FIXEDWINDOW, MULTISCALE, LAB));
        // get bounding boxes

        init(box, refer_frame);

        //traj.trajectory.emplace_back(x->frame_id, box);
        int current_frame = x->frame_id;
        bool is_match = false;
        for (const auto &item : x->after_frame_trackers) {
            EdgeBox old_tracker_box = item->traj.get_init_frame_box();
            int old_tracker_frame_id = item->traj.get_init_frame_id();
            if (old_tracker_box.class_name == box.class_name) {
                EdgeBox b;
                while (old_tracker_frame_id > current_frame) {
                    current_frame += detector_skip;
                    shared_ptr<EdgeFrame> updated_frame = x->framePool->frames[current_frame];
                    b = update(updated_frame);
                    traj.trajectory.emplace_back(current_frame, b);
                }
                assert(old_tracker_frame_id == current_frame);
                if (box.calculate_iou(old_tracker_box) >= iou_thres) {
                    is_match = true;
                    break;
                }
            }
        }
        if (is_match) {
            status = TRACKER_INVALID;
        }else{
            status = TRACKER_VALID;
        }
    }
}

void BaseSingleTracker::reset_tracker() {
    if(status == TRACKER_RESET) {
        // printf("reset tracker...\n");
        auto x = resetArgs;
        shared_ptr<EdgeFrame> refer_frame = x->framePool->frames[x->frame_id];
        EdgeBox box = x->box;
        // get bounding boxes
        reset(box, refer_frame);
        // remove trajectory bigger than frame_id
        // traj.remove_bigger_frame(x->frame_id);
        // traj.trajectory.emplace_back(x->frame_id, x->box);
        //pthread_exit(NULL);
        status = TRACKER_VALID;
    }
}

void* BaseSingleTracker::update_tracker_thread(void *args) {


    auto x = (UpdateTrackerArgs *) args;
    auto start_time = Utils::current_time();
    //if run time is finished exit
    int detector_skip = x->detector_skip;
    auto last_item = traj.trajectory[traj.trajectory.size() - 1];
    auto last_frame_id = get<0>(last_item);
    if (start_time - x->start_time >= x->max_duration) {
        x->updated_box = get<1>(last_item);
        x->is_update = false;
        return nullptr;
    }

    new_tracker();
    reset_tracker();
    
    assert(last_frame_id < x->frame_id);
    
    
    int update_frame_id = last_frame_id + 1;
    x->is_update = true;
    EdgeBox box = traj.get_init_frame_box();
    while (update_frame_id < x->frame_id) {
        if (update_frame_id % detector_skip == 0) {
            auto img = x->framePool->frames[update_frame_id];
            EdgeBox b = update(img);
            traj.trajectory.emplace_back(update_frame_id, b);
            //x->updated_box = b;
        }
        update_frame_id += 1;
    }
    auto update_img = x->framePool->frames[x->frame_id];
    
    EdgeBox b = update(update_img);
    x->updated_box = b;
    traj.trajectory.emplace_back(x->frame_id, b);
    // update priority score
    x->myL = runtime_priority;
    update_priority();

    return nullptr;
}
