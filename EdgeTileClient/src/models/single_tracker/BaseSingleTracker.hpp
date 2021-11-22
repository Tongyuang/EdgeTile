//
// Created by Xu Wang on 2020/4/11.
//

#ifndef EDGETILECPP_BASESINGLETRACKER_HPP
#define EDGETILECPP_BASESINGLETRACKER_HPP

#include "opencv2/opencv.hpp"
#include "../../datatype/EdgeBox.hpp"
#include "../../datatype/EdgeTraj.hpp"
#include "../../datatype/EdgeFrame.hpp"

using namespace cv;
using namespace Edge;

enum TrackerStatus {
    TRACKER_INIT = 0,
    TRACKER_VALID = 1,
    TRACKER_RESET=2,
    TRACKER_INVALID=3
};
namespace Edge {
    class NewTrackerArgs;

    class ResetTrackerArgs;

    class UpdateTrackerArgs;
}

class BaseSingleTracker {
public:
    explicit BaseSingleTracker();

    virtual EdgeBox update(shared_ptr<EdgeFrame>) = 0;

    virtual void init(EdgeBox box, shared_ptr<EdgeFrame> frame) = 0;

    virtual void reset(EdgeBox box, shared_ptr<EdgeFrame> frame) = 0;

    int bigL;

    int globalL;

    int priority_seed;

    int runtime_priority;

    bool is_server;

    int mismatch;

    int tracker_id;

    int recent_detect_frame;

    EdgeBox recent_detect_box;

    EdgeTraj traj;

    TrackerStatus status;

    shared_ptr<NewTrackerArgs> newArgs;
    shared_ptr<ResetTrackerArgs> resetArgs;

    float priority_score(int frame_id);

    void update_priority();

    void new_tracker();

    void reset_tracker();

    void* update_tracker_thread(void* args);

};


#endif //EDGETILECPP_BASESINGLETRACKER_HPP
