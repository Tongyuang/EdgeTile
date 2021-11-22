//
// Created by Xu Wang on 2019/12/16.
//

#ifndef EDGETILECPP_EDGEQUEUE_HPP
#define EDGETILECPP_EDGEQUEUE_HPP
#include "concurrentqueue/blockingconcurrentqueue.h"
#include "../datatype/EdgeFrame.hpp"

namespace Edge {
    class EdgeQueue {
    public:
        void put(shared_ptr<EdgeFrame> item);

        shared_ptr<EdgeFrame> get();

        int queue_size();

        string queue_name;

    private:
        moodycamel::BlockingConcurrentQueue<shared_ptr<EdgeFrame>> q;
    };
}


#endif //EDGETILECPP_EDGEQUEUE_HPP
