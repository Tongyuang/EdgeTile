//
// Created by Xu Wang on 2019/12/16.
//

#include "EdgeQueue.hpp"
#include "Utils.hpp"
using namespace Edge;

shared_ptr<EdgeFrame> EdgeQueue::get() {
    //printf("%s try get item\n", queue_name.c_str());
    shared_ptr<EdgeFrame> output;
    q.wait_dequeue(output);
    //printf("%s get item success\n", queue_name.c_str());
    return output;
}

void EdgeQueue::put(shared_ptr<EdgeFrame> item) {
    shared_ptr <EdgeFrame> tmp;
    // while (q.try_dequeue(tmp));
    q.enqueue(item);
}

int EdgeQueue::queue_size(){
    return q.size_approx();
}