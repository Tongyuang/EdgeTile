//
// Created by Xu Wang on 2020/5/30.
//

#ifndef EDGETILECPP_EDGEVIDEO_HPP
#define EDGETILECPP_EDGEVIDEO_HPP
#include "EdgePacket.hpp"
namespace Edge {
    class EdgeVideo :public EdgePacket{
    public:
        EdgeVideo();

        EdgeVideo(const EdgeVideo& video);

        string file_path;
        int width;
        int height;
        int fps;

    };
}



#endif //EDGETILECPP_EDGEVIDEO_HPP
