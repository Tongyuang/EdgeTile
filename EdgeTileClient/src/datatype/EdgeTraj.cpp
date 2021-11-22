//
// Created by Xu Wang on 2020/5/30.
//

#include "EdgeTraj.hpp"
using namespace Edge;

int EdgeTraj::get_init_frame_id() {
    return get<0>(trajectory[0]);
}

EdgeBox EdgeTraj::get_init_frame_box() {
    return get<1>(trajectory[0]);
}

EdgeBox EdgeTraj::get_frame_box(int frame_id) {
    int pos = 0;
    for(int i = 0; i < trajectory.size(); i ++){
        if(get<0>(trajectory[i]) <= frame_id){
            pos = i;
        }else{
            break;
        }
    }
    return get<1>(trajectory[pos]);
}

void EdgeTraj::remove_bigger_frame(int frame_id) {
    int n = 0;
    for(auto x: trajectory){
        if(get<0>(x) < frame_id){
            n += 1;
        }else{
            break;
        }
    }
    trajectory.resize(n);
}

int EdgeTraj::get_last_frame_id() {
    return get<0>(trajectory[trajectory.size() - 1]);
}
