//
// Created by Xu Wang on 2020/5/30.
//

#include "EdgeVideo.hpp"
using namespace Edge;

EdgeVideo::EdgeVideo(): EdgePacket("EdgeVideo") {

}

EdgeVideo::EdgeVideo(const EdgeVideo &video) : EdgePacket("EdgeVideo"){
    file_path = video.file_path;
    width = video.width;
    height = video.height;
    fps = video.fps;
}