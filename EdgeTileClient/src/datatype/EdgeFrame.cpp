//
// Created by Xu Wang on 2019/12/16.
//

#include "EdgeFrame.hpp"
#include <pugixml.hpp>
#include <fstream>
using namespace Edge;
using namespace cv;
using namespace pugi;
#include <iostream>
#include "../utils/Utils.hpp"

EdgeFrame::EdgeFrame():EdgePacket("EdgeFrame")
{
    frame_idx = -1;
    in_blacklist = true;
    will_upload = false;
    is_track_finished = false;
}

void EdgeFrame::convert_rgb2yuv()
{
    cvtColor(raw_frame, yuv_data, COLOR_BGR2YUV_I420);

    int height = raw_frame.size[0];

    auto y = yuv_data(Range(0, height), Range::all()).reshape(0, 1);
    auto u = yuv_data(Range(height, int(height + height / 4)), Range::all()).reshape(0, 1);
    auto v = yuv_data(Range(int(height + height / 4), yuv_data.size[0]), Range::all()).reshape(0, 1);

    yuv_frame.push_back(y);
    yuv_frame.push_back(u);
    yuv_frame.push_back(v);
}

vector<EdgeBox> load_pre_bboxes(string frame_anno_path){
    vector<EdgeBox> gt_bboxes;
    xml_document doc;
    xml_parse_result result = doc.load_file(frame_anno_path.data());
    if (!result)
    {
        printf("xml_parse_result NO RESULT!\n");
        return gt_bboxes;
    }

    xpath_node_set objects = doc.select_nodes(".//object");
    for (xpath_node node : objects)
    {
        EdgeBox b;
        xml_node obj = node.node();
        b.track_id = obj.select_node("./trackid").node().text().as_int();
        b.xmax = obj.select_node(".//xmax").node().text().as_int();
        b.xmin = obj.select_node(".//xmin").node().text().as_int();
        b.ymax = obj.select_node(".//ymax").node().text().as_int();
        b.ymin = obj.select_node(".//ymin").node().text().as_int();
        b.class_name = obj.select_node("./name").node().text().as_string();
        b.confidence = 1.0;
        gt_bboxes.push_back(b);
    }
    return gt_bboxes;
}
void EdgeFrame::load_bboxes(string file_path,string file_path2)
{
    xml_document doc;
    xml_parse_result result = doc.load_file(file_path.data());
    if (!result)
    {
        printf("xml_parse_result NO RESULT!\n");
        return;
    }

    xpath_node_set objects = doc.select_nodes(".//object");
    for (xpath_node node : objects)
    {
        EdgeBox b;
        xml_node obj = node.node();
        b.track_id = obj.select_node("./trackid").node().text().as_int();
        b.xmax = obj.select_node(".//xmax").node().text().as_int();
        b.xmin = obj.select_node(".//xmin").node().text().as_int();
        b.ymax = obj.select_node(".//ymax").node().text().as_int();
        b.ymin = obj.select_node(".//ymin").node().text().as_int();
        b.class_name = obj.select_node("./name").node().text().as_string();
        b.confidence = 1.0;
        float box_size = (b.xmax-b.xmin)*(b.ymax-b.ymin);

        this->gt_bboxes.push_back(b);

            
        // EdgeBox pre_box;
        // bool exist_track_id = false;
        // vector<EdgeBox> preBoxes = load_pre_bboxes(file_path2);
        // for(int k = 0; k < preBoxes.size();k++){
        //     if(preBoxes[k].track_id == b.track_id){
        //         pre_box = preBoxes[k];
        //         exist_track_id  = true;
        //         break;
        //     }
        // }
        // if(exist_track_id == true){
        //     float x1 = (pre_box.xmin+pre_box.xmax)/2.0;
        //     float y1 = (pre_box.ymin+pre_box.ymax)/2.0;
        //     float x2 = (b.xmin+b.xmax)/2.0;
        //     float y2 = (b.ymin+b.ymax)/2.0;
        //     float speed = sqrt(pow(x2-x1,2)+pow(y2-y1,2));
        //     if(speed < 10 || speed > 20){
        //         continue;
        //     }
        // }else{
        //     continue;
        // }
            
        
        

    }
}
void EdgeFrame::load_motionVectors(string file_path) {
    // read a JSON file
    std::ifstream i(file_path.c_str());
    json j;
    i >> j;
    for(auto vec: j){
        map<string, int> item;
        int src_x = vec["src_x"];
        int src_y = vec["src_y"];
        int dst_x = vec["dst_x"];
        int dst_y = vec["dst_y"];
        item["src_x"] = src_x;
        item["src_y"] = src_y;
        item["dst_x"] = dst_x;
        item["dst_y"] = dst_y;
        // printf("motion vector:<(%d,%d),(%d,%d)>\n", src_x,src_y,dst_x,dst_y);
        this->motion_vectors.push_back(item);
    }
}

void EdgeFrame::load_local_detect_bboxes(string file_path)
{
    xml_document doc;
    xml_parse_result result = doc.load_file(file_path.data());
    if (!result)
    {
        printf("xml_parse_result NO RESULT!\n");
        return;
    }

    xpath_node_set objects = doc.select_nodes(".//object");
    for (xpath_node node : objects)
    {
        EdgeBox b;
        xml_node obj = node.node();
        b.track_id = obj.select_node("./trackid").node().text().as_int();
        b.xmax = obj.select_node(".//xmax").node().text().as_int();
        b.xmin = obj.select_node(".//xmin").node().text().as_int();
        b.ymax = obj.select_node(".//ymax").node().text().as_int();
        b.ymin = obj.select_node(".//ymin").node().text().as_int();
        b.class_name = obj.select_node("./name").node().text().as_string();
        b.confidence = obj.select_node("./confidence").node().text().as_float();
        float box_size = (b.xmax-b.xmin)*(b.ymax-b.ymin);

        this->local_detect_bboxes.push_back(b);

    }
}

cv::Mat EdgeFrame::render()
{
    // to do by wjh
    //draw gt_bbox, server_bbox, client_bblox on frame
    cv::Mat m;
    return m;
}

vector<EdgeBox> EdgeFrame::diff_local_bboxes(vector<EdgeBox> boxes, double thres) {
    vector<EdgeBox> filterBoxes;
//    if(local_bboxes.size() <= 0){
//        int x = 0;
//        for(auto b: boxes){
//            if(b.class_name == "pedestrian"){
//                filterBoxes.push_back(b);
//            }else if(x == 0){
//                filterBoxes.push_back(b);
//                x = 1;
//            }
//        }
//        return filterBoxes;
//    }

    for(auto b1 : boxes){
        bool is_match = false;
        for(auto b2: local_bboxes){
            if(b1.class_name == b2.class_name){
                float x = b1.calculate_iou(b2);
                if(x >= thres){
                    is_match = true;
                    break;
                }
            }
        }
        if(!is_match){
            filterBoxes.push_back(b1);
        }
    }
    return filterBoxes;
}
