//
// Created by Xu Wang on 2019/12/16.
//

#ifndef EDGETILECPP_EDGEBOX_HPP
#define EDGETILECPP_EDGEBOX_HPP

#include <string>
#include "nlohmann/json.hpp"
#include "opencv2/opencv.hpp"
#include "EdgePacket.hpp"

using namespace std;
using namespace nlohmann;

namespace Edge {
    class EdgeBox : public EdgePacket {
    public:
        float xmin;
        float xmax;
        float ymin;
        float ymax;
        vector<cv::Point2f> key_points;
        int track_id;
        float confidence;
        string class_name;
        bool is_server;
    public:
        static vector<EdgeBox *> load(string file_path);

        EdgeBox(json j);

        EdgeBox() : EdgePacket("EdgeBox") {}

        float intersectRectPercentage(cv::Rect2d r);

        float calculate_iou(EdgeBox &r);
    };

    class EdgeBoxArray : public EdgePacket {
    public:
        EdgeBoxArray() : EdgePacket("EdgeBoxArray") {
            frame_id = -1;
            group_id = -1;
            level = "";
        }
        bool is_server;
        vector<EdgeBox> boxes;
        int frame_id;
        int group_id;
        string level;
    };
}


#endif //EDGETILECPP_EDGEBOX_HPP
