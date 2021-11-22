//
// Created by Xu Wang on 2020/5/30.
//

#ifndef EDGETILECPP_EDGETRAJ_HPP
#define EDGETILECPP_EDGETRAJ_HPP
#include "EdgePacket.hpp"
#include "EdgeBox.hpp"

namespace Edge {
    class EdgeTraj : public EdgePacket {
    public:

        vector<tuple<int, EdgeBox>> trajectory;

        EdgeTraj() : EdgePacket("EdgeTraj") {

        }
        int get_init_frame_id();

        int get_last_frame_id();

        EdgeBox get_init_frame_box();

        EdgeBox get_frame_box(int frame_id);

        void remove_bigger_frame(int frame_id);
    };
}


#endif //EDGETILECPP_EDGETRAJ_HPP
