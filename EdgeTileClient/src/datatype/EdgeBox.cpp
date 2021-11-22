//
// Created by Xu Wang on 2019/12/16.
//

#include "EdgeBox.hpp"
#include <iostream>

using namespace Edge;
using namespace cv;
EdgeBox::EdgeBox(json j): EdgePacket("EdgeBox") {
    vector<string> attrs = {"class_name", "xmin", "xmax", "ymin", "ymax", "track_id", "confidence","key_points"};
    for(int i = 0; i < attrs.size(); i ++){
        auto attr = attrs[i];
        if(j.find(attr) != j.end()){
            switch (i){
                case 0:
                {
                    class_name = j[attr];
                    break;
                }
                case 1:
                {
                    xmin = j[attr];
                    break;
                }
                case 2:
                {
                    xmax = j[attr];
                    break;
                }
                case 3:
                {
                    ymin = j[attr];
                    break;
                }
                case 4:
                {
                    ymax = j[attr];
                    break;
                }
                case 5:
                {
                    track_id = j[attr];
                    break;
                }
                case 6:
                {
                    confidence = j[attr];
                    break;
                }
                case 7:
                {
                    
                    for(int i = 0; i < j[attr].size(); i++){
                        float a = j[attr][i][0];
                        float b = j[attr][i][1];
                        cv::Point2f point(a,b);
                        key_points.push_back(point);
                    }
                    break;
                }
            }
        }
    }
}

float EdgeBox::intersectRectPercentage(cv::Rect2d r) {
    Rect2d box;
    box.x = xmin, box.y = ymin, box.width = xmax - xmin, box.height = ymax - ymin;
    return (box & r).area() / box.area();
}

float EdgeBox::calculate_iou(EdgeBox& r) {
    Rect2d box;
    box.x = xmin, box.y = ymin, box.width = xmax - xmin, box.height = ymax - ymin;
    Rect2d box2;
    box2.x = r.xmin, box2.y = r.ymin, box2.width = r.xmax - r.xmin, box2.height = r.ymax - r.ymin;
    double a = (box & box2).area();
    return a / (box.area() + box2.area() - a);
}
