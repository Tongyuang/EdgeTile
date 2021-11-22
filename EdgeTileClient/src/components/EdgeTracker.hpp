//
// Created by Xu Wang on 2019/12/17.
//

#ifndef EDGETILECPP_EDGETRACKER_HPP
#define EDGETILECPP_EDGETRACKER_HPP

#include "../EdgeComponent.hpp"
#include "../utils/EdgeQueue.hpp"
#include "../models/single_tracker/BaseSingleTracker.hpp"
#include "../datatype/EdgeFramePool.hpp"


using namespace cv;

namespace Edge {
    class EdgeApp;

    class NewTrackerArgs {
    public:
        int frame_id;
        EdgeBox box;
        int detector_skip;
        float iou_thres;
        vector<shared_ptr<BaseSingleTracker>> after_frame_trackers;
        shared_ptr<EdgeFramePool> framePool;
        int realtimeL;
    };

    class ResetTrackerArgs {
    public:
        int frame_id;
        EdgeBox box;
        shared_ptr<EdgeFramePool> framePool;
    };

    class UpdateTrackerArgs {
    public:
        long long start_time;
        float max_duration;// ms
        int frame_id;
        int detector_skip;
        shared_ptr<EdgeFramePool> framePool;
        EdgeBox updated_box;
        bool is_update;
        int myL;
    };

    class EdgeTracker : public EdgeComponent {
    public:
        explicit EdgeTracker(EdgeApp *app);

        ~EdgeTracker();

        void initialize() override;

        void run() override;

        vector<shared_ptr<BaseSingleTracker>> sorted_trackers; // keep order by the init frame id


        shared_ptr<EdgeFramePool> framePool;

        void update_reference_bbox(shared_ptr<EdgeBoxArray> boxArray);

        void update_trackers(shared_ptr<EdgeBoxArray> boxArray);


        void detect(shared_ptr<EdgeFrame> f);

        void *new_tracker_thread(void *args);

        void *reset_tracker_thread(void *args);

        void *update_tracker_thread(void *args);

        vector<shared_ptr<BaseSingleTracker>> get_priority_trackers(int frame_id);

        int get_new_tracker_id();

        void free_mat(int frame_id);

        int last_free_mat;

        moodycamel::ConcurrentQueue<shared_ptr<EdgeBoxArray>> readyBoxArray;

        int realtimeL;

    private:
        //BaseMultiTracker *model;
        mutex *visitLock;
        int tracker_counter;
    };
}


#endif //EDGETILECPP_EDGETRACKER_HPP
