//
// Created by 吴家行 on 2020/8/5.
//

#ifndef EDGETILECPP_MVTRACKERWRAPPER_H
#define EDGETILECPP_MVTRACKERWRAPPER_H
#include "BaseSingleTracker.hpp"
using namespace std;

class MVTrackerWrapper: public BaseSingleTracker {
public:
    explicit MVTrackerWrapper();
    EdgeBox update(shared_ptr<EdgeFrame> frame);
    void init(EdgeBox rect, shared_ptr<EdgeFrame> frame);
    void reset(EdgeBox rect, shared_ptr<EdgeFrame> frame);
    Rect2d currentRect;

};


#endif //EDGETILECPP_MVTRACKERWRAPPER_H
