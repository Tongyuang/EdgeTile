//
// Created by Xu Wang on 2019/12/16.
//

#ifndef EDGETILECPP_EDGESTREAMER_HPP
#define EDGETILECPP_EDGESTREAMER_HPP
#include <opencv2/opencv.hpp>
#include <string>
#include "../EdgeComponent.hpp"
#include "../datatype/EdgeVideo.hpp"

using namespace std;
using namespace cv;

namespace Edge {

    class EdgeApp;

    enum EdgeStreamerStatus {
        STREAMER_NO_PLAY = 0,
        STREAMER_IS_PLAY = 1
    };

    class EdgeStreamer : public EdgeComponent {
    public:
        explicit EdgeStreamer(EdgeApp *app);

        ~EdgeStreamer() { delete cap; }

        EdgeStreamerStatus status;

        void initialize() override;

        void run() override;

        cv::VideoCapture *cap;

        EdgeVideo videoAttrs;

        int readFrames;

    private:
        bool next_frame();
    };
}


#endif //EDGETILECPP_EDGESTREAMER_HPP