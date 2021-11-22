//
// Created by Xu Wang on 2020/4/11.
//

#ifndef EDGETILECPP_KCFTRACKERWRAPPER_HPP
#define EDGETILECPP_KCFTRACKERWRAPPER_HPP
#include "../kcf_tracker/kcftracker.hpp"
#include "BaseSingleTracker.hpp"
using namespace std;

class KCFTrackerWrapper:public BaseSingleTracker {
public:
    explicit KCFTrackerWrapper(bool hog = true, bool fixed_window = true, bool multiscale = true, bool lab = true);
    EdgeBox update(shared_ptr<EdgeFrame> frame);
    void init(EdgeBox rect, shared_ptr<EdgeFrame> frame);
    void reset(EdgeBox rect, shared_ptr<EdgeFrame> frame);
    bool hog;
    bool fixed_window;
    bool multiscale;
    bool lab;
private:
    shared_ptr<KCFTracker> tracker;

};


#endif //EDGETILECPP_KCFTRACKERWRAPPER_HPP
