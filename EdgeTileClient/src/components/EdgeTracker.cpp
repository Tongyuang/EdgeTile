//
// Created by Xu Wang on 2019/12/17.
//

#include "EdgeTracker.hpp"
#include "../models/single_tracker/KcfTrackerWrapper.hpp"
#include "../utils/Utils.hpp"
#include "../EdgeApp.hpp"
#include "../utils/threadpool/ThreadPool.h"
#include "../include/EdgeClient.hpp"

using namespace Edge;

EdgeTracker::EdgeTracker(Edge::EdgeApp *app) : EdgeComponent(app, "tracker") {
    dataQueue.queue_name = "readyTrackingFrames";
    visitLock = new mutex();
    tracker_counter = 0;
    last_free_mat = -1;
    realtimeL = 0;
}

EdgeTracker::~EdgeTracker() = default;

void EdgeTracker::initialize() {

}

void EdgeTracker::free_mat(int frame_id) {
    if(last_free_mat + 1 >= frame_id){
        return;
    }
    int min_frame = INT_MAX;

    for(auto tracker : sorted_trackers){
        auto fid = tracker->traj.get_last_frame_id();
        if(fid < min_frame){
            min_frame = fid - 1;
        }
    }
    min_frame = min(min_frame, frame_id - 1);
    while(last_free_mat + 1 < min_frame){
        last_free_mat = last_free_mat + 1;
        framePool->frames[last_free_mat]->raw_frame.release();
        edge_logger->logger->info("release frame:{}", last_free_mat);
    }
}

void EdgeTracker::run() {
    while (!is_stopped()) {
        bool found = true;
        while(found) {
            shared_ptr<EdgeBoxArray> item;
            found = readyBoxArray.try_dequeue(item);
            if (found) {
                auto start_time = Utils::current_time();
                update_trackers(item);
                auto time_cost = Utils::current_time() - start_time;
                edge_logger->logger->info(fmt::format("update log-- frame[{0}] tile[{1}] results time cost: {2} ms",
                item->frame_id, item->group_id, time_cost));
            }
        }
        auto f = dataQueue.get();
        if (f->frame_idx < 0) {
            EdgeClient* client = (EdgeClient*)(this->app);
            edge_logger->logger->info("export tracking box to evaluate...");
            client->evaluate(0.5);

            client->get_framePool()->export_read_timestamps();
            client->get_framePool()->export_recv_timestamps();
            client->get_framePool()->export_client_boxes();
            client->get_framePool()->export_tracking_boxes_to_xml();
            printf("over!\n");
            break;
        } else {
            visitLock->lock();
            if (!sorted_trackers.empty()) {
                f->in_blacklist = false;
                long long c_time = Utils::current_time();
                edge_logger->logger->info(fmt::format("*bbox_track_start frame: {0}", f->frame_idx));
                detect(f);
                f->is_track_finished = true;
                edge_logger->logger->info(fmt::format("*bbox_track_end frame: {0}", f->frame_idx));
                long long total_track_time;
                total_track_time = Utils::current_time() - c_time;
                edge_logger->logger->info(fmt::format("tracker TIME COST：{}ms", total_track_time));
                yield(f);
            }
            visitLock->unlock();
        }
    }
    edge_logger->logger->info("tracking thread exit...");
}

void EdgeTracker::update_reference_bbox(shared_ptr<EdgeBoxArray> boxArray) {
    readyBoxArray.enqueue(boxArray);
}

void EdgeTracker::update_trackers(shared_ptr<EdgeBoxArray>boxArray){
    visitLock->lock();
    float iou_thres = stof(config["iou_thres"].Scalar());
    int encoder_skip = stoi(app->config["encoder_skip"].Scalar());
    int frame_id = boxArray->frame_id;
    if(boxArray->is_server || app->config["detector_mode"].Scalar()=="local"){
        free_mat(frame_id);
    }


    vector<shared_ptr<BaseSingleTracker>> trackers_before_frame;

    vector<shared_ptr<BaseSingleTracker>> trackers_after_frame;
    //
    for (auto x : sorted_trackers) {
        if (x->traj.get_init_frame_id() <= frame_id) {
            trackers_before_frame.push_back(x);
        } else {
            trackers_after_frame.push_back(x);
        }
    }
    //get edge box for frame_id
    vector<EdgeBox> before_bboxes;
    for (auto x: trackers_before_frame) {
        before_bboxes.push_back(x->traj.get_frame_box(frame_id));
    }
    
    vector<tuple<int, int, float>> iou_matrix;
    for (int i = 0; i < boxArray->boxes.size(); i++) {
        for (int j = 0; j < before_bboxes.size(); j++) {
            if (boxArray->boxes[i].class_name == before_bboxes[j].class_name) {
                float iou = boxArray->boxes[i].calculate_iou(before_bboxes[j]);
                if (iou >= iou_thres) {
                    iou_matrix.emplace_back(i, j, iou);
                }
            }
        }
    }
    // sort by iou value
    sort(iou_matrix.begin(), iou_matrix.end(),
         [](const tuple<int, int, float> &a, const tuple<int, int, float> &b) -> bool {
             return get<2>(a) > get<2>(b);
         });
    set<int> detector_box;
    set<int> tracker_box;
    vector<tuple<int, int, float>> matched_box;
    for (auto &item : iou_matrix) {
        int x = get<0>(item);
        int y = get<1>(item);
        if (detector_box.find(x) == detector_box.end() && tracker_box.find(y) == tracker_box.end()) {
            matched_box.push_back(item);
            detector_box.insert(x);
            tracker_box.insert(y);
        }
    }
    string recv_from;
    if (boxArray->is_server) {
        recv_from = "Server";
    } else {
        recv_from = "Client";
    }

    
    edge_logger->logger->info(fmt::format("recv from {0}: matched box number:{1}",
                                          recv_from, detector_box.size()));
    // un matched server box
    vector<int> no_match_boxes;
    for (int i = 0; i < boxArray->boxes.size(); i++) {
        if (detector_box.find(i) == detector_box.end()) {
            no_match_boxes.push_back(i);
        }
    }
    int num_threads = no_match_boxes.size();


    vector<shared_ptr<BaseSingleTracker>> matched_new_trackers;
    for (int i = 0; i < num_threads; ++i) {
        shared_ptr<NewTrackerArgs> new_args = shared_ptr<NewTrackerArgs>(new NewTrackerArgs());
        new_args->frame_id = frame_id;
        new_args->after_frame_trackers = trackers_after_frame;
        new_args->framePool = framePool;
        new_args->box = boxArray->boxes[no_match_boxes[i]];
        new_args->detector_skip = stoi(app->config["detector_skip"].Scalar());
        new_args->iou_thres = stof(config["iou_thres"].Scalar());
        new_args->realtimeL = realtimeL;
        bool HOG = false;
        bool FIXEDWINDOW = true;
        bool MULTISCALE = false;
        bool LAB = false; // 开启会变慢
        // Create KCFTracker object
        shared_ptr<BaseSingleTracker> tracker = shared_ptr<KCFTrackerWrapper>(new KCFTrackerWrapper(HOG, FIXEDWINDOW, MULTISCALE, LAB));
        tracker->newArgs = new_args;
        tracker->status = TRACKER_INIT;
        tracker->tracker_id = get_new_tracker_id();
        tracker->is_server = boxArray->is_server;
        tracker->traj.trajectory.emplace_back(frame_id, new_args->box);
        tracker->recent_detect_frame = frame_id;
        matched_new_trackers.push_back(tracker);
    }

    vector<tuple<int, int, float>> filter_matched_box;
    for(auto item: matched_box){
        int x = get<0>(item);
        int y = get<1>(item);
        auto tracker = trackers_before_frame[y];
        if(tracker->recent_detect_frame < frame_id){
            filter_matched_box.push_back(item);
        }
    }
    // for matched client box

    int num_threads2 = filter_matched_box.size();

    for (int i = 0; i < num_threads2; ++i) {
        int x = get<0>(filter_matched_box[i]);
        int y = get<1>(filter_matched_box[i]);
        shared_ptr<ResetTrackerArgs> reset_args = shared_ptr<ResetTrackerArgs>(new ResetTrackerArgs());
        auto tracker = trackers_before_frame[y];
        reset_args->frame_id = frame_id;
        reset_args->framePool = framePool;
        reset_args->box = boxArray->boxes[x];
        // remove trajectory bigger than frame_id
        tracker->traj.remove_bigger_frame(frame_id);
        tracker->traj.trajectory.emplace_back(frame_id,  boxArray->boxes[x]);
        tracker->recent_detect_frame = frame_id;
        tracker->resetArgs = reset_args;
        tracker->status = TRACKER_RESET;
    }
    // clean long time no detect trackers

    // update trackers
    if (!matched_new_trackers.empty()) {
        trackers_before_frame.insert(trackers_before_frame.end(), matched_new_trackers.begin(),
                                     matched_new_trackers.end());
        trackers_before_frame.insert(trackers_before_frame.end(), trackers_after_frame.begin(),
                                     trackers_after_frame.end());
        vector<shared_ptr<BaseSingleTracker>> filter_trackers;
        for(auto t: trackers_before_frame){
            if(frame_id - t->recent_detect_frame <= encoder_skip){
                // keep
                filter_trackers.push_back(t);
            }
        }
        sorted_trackers = filter_trackers;
    }
    visitLock->unlock();

//printf("objects: %lu\n", objects.size());
}


vector<shared_ptr<BaseSingleTracker>> EdgeTracker::get_priority_trackers(int frame_id) {
    vector<tuple<float, shared_ptr<BaseSingleTracker>>> trackers;
    for (auto x: sorted_trackers) {
        float pr = x->priority_score(frame_id);
        trackers.emplace_back(pr, x);
    }
    sort(trackers.begin(), trackers.end(),
         [](const tuple<float, shared_ptr<BaseSingleTracker>> &a,
            const tuple<float, shared_ptr<BaseSingleTracker>> &b) -> bool {
             return get<0>(a) < get<0>(b);
         });
    vector<shared_ptr<BaseSingleTracker>> res;
    for (auto x: trackers) {
        res.push_back(get<1>(x));
    }
    return res;
}


void EdgeTracker::detect(shared_ptr<EdgeFrame> f) {

    vector<EdgeBox> boundingBoxes;
    auto start_time = Utils::current_time();
    // order tracker by priority
    auto trackers = get_priority_trackers(f->frame_idx);
    int num_threads = trackers.size();
    // int num_threads = min(10, (int)trackers.size());
    UpdateTrackerArgs data[num_threads];
    ThreadPool pool(4);
    std::vector<std::future<bool> > results;
    auto edge_tracker = this;
    int tracker_limit = stoi(app->config["tracker_limit"].Scalar());
    int fps = stoi(app->config["fps"].Scalar());
    printf("tracker_limit:%d fps:%d\n", tracker_limit, fps);
    for (int i = 0; i < num_threads; ++i) {
        auto tracker = trackers[i];
        data[i].framePool = framePool;
        data[i].frame_id = f->frame_idx;
        data[i].start_time = start_time;
        if(i >= tracker_limit){
            data[i].max_duration = 0;
        }else{
            data[i].max_duration = 1000.0;
        }


        data[i].detector_skip = stoi(app->config["detector_skip"].Scalar());
        results.emplace_back(
                pool.enqueue([i, tracker](UpdateTrackerArgs *x) {
                    tracker->update_tracker_thread(x);
                    return true;
                }, &data[i])
        );
    }

    //  更新f的client_bboxes
    // edge_logger->logger->info(
    //         fmt::format("frame {0} enqueue pool done. num_threads={1}", f->frame_idx, num_threads));
    int update_count = 0;
    for (int i = 0; i < num_threads; ++i) {
        results[i].get();
        // edge_logger->logger->info(
        //     fmt::format("frame {0} get result {1}/{2}", f->frame_idx, i, num_threads));
        f->client_bboxes.push_back(data[i].updated_box);
        if(data[i].is_update){
            update_count += 1;
            realtimeL = max(realtimeL, data[i].myL);
        }
    }

    //  更新所有的tracker
    vector<shared_ptr<BaseSingleTracker>> filter_trackers;
    for(auto tracker: sorted_trackers){
        if(tracker->status != TRACKER_INVALID){
            filter_trackers.push_back(tracker);
        }
    }
    sorted_trackers = filter_trackers;
    auto time_cost = Utils::current_time() - start_time;
    edge_logger->logger->info(
            fmt::format("tracking update: frame id: {0} tracker numbers:{1} time:{2}ms fps:{3} real update: {4}/{5}",
                        f->frame_idx, boundingBoxes.size(), time_cost, (int) (1000 / time_cost), update_count, num_threads));

}


int EdgeTracker::get_new_tracker_id() {
    int t = tracker_counter;
    tracker_counter += 1;
    return t;
}
