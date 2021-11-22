//
// Created by Xu Wang on 2020/5/30.
//

#include "EdgeFramePool.hpp"
#include "../include/EdgeClient.hpp"
#include <pugixml.hpp>
#include <iostream>
#include <unistd.h>
#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include <sys/stat.h>
#include <stdlib.h>

using namespace Edge;

void Getfilepath(const char *path, const char *filename,  char *filepath)
{
    strcpy(filepath, path);
    if(filepath[strlen(path) - 1] != '/')
        strcat(filepath, "/");
    strcat(filepath, filename);
	// printf("path is = %s\n",filepath);
}
 
bool DeleteFile(const char* path)
{
    DIR *dir;
    struct dirent *dirinfo;
    struct stat statbuf;
    char filepath[256] = {0};
    lstat(path, &statbuf);
    
    if (S_ISREG(statbuf.st_mode))//判断是否是常规文件
    {
        remove(path);
    }
    else if (S_ISDIR(statbuf.st_mode))//判断是否是目录
    {
        if ((dir = opendir(path)) == NULL)
            return 1;
        while ((dirinfo = readdir(dir)) != NULL)
        {
            Getfilepath(path, dirinfo->d_name, filepath);
            if (strcmp(dirinfo->d_name, ".") == 0 || strcmp(dirinfo->d_name, "..") == 0)//判断是否是特殊目录
            continue;
            DeleteFile(filepath);
            rmdir(filepath);
        }
        closedir(dir);
    }
    return 0;
}
EdgeFramePool::EdgeFramePool(EdgeApp *app): EdgePacket("EdgeFramePool")
{
    this->app = app;
    last_free_frame = -1;
}


double EdgeFramePool::calculate_fps(int last_frame) {
    if(last_frame > 0 && (this->frames[last_frame]->before_render_time - this->frames[last_frame - 1]->before_render_time) > 0){
        return 1000 / (this->frames[last_frame]->before_render_time - this->frames[last_frame - 1]->before_render_time);
    }
    return 0;
}

void EdgeFramePool::export_tracking_boxes() {
//    class_name = 'pedestrian'
//    pred_file = open(f'data/drone/{class_name}.txt', 'w')
    // each class has one file
    EdgeClient* client = (EdgeClient*) app;
    map<string, FILE*> each_class_res;
    FILE* imgSet_handler;
    auto exp_dir = this->app->get_file_path(path(app->config["exp_dir"].Scalar()));
    client->edge_logger->logger->info("writing to exp_dir:{}", exp_dir.string());
    if(!exists(exp_dir)){
        client->edge_logger->logger->info("try to create exp_dir:{}", exp_dir.string());
        create_directory(exp_dir);
        client->edge_logger->logger->info("success to create exp_dir:{}", exp_dir.string());
    }
    auto imgSet_path = exp_dir / "img_set.txt";
    client->edge_logger->logger->info("start to write file: {}", imgSet_path.string());
    imgSet_handler = fopen(imgSet_path.c_str(), "w+");
    client->edge_logger->logger->info("start2 to write file: {}", imgSet_path.string());
    for(auto f : frames){
        if(f->frame_idx < 0)continue;
        if(f->client_bboxes.size()>0){
            string content = fmt::format("{:06d}\n", f->frame_idx);
            fwrite(content.data(), sizeof(char), content.length(), imgSet_handler);
            for(auto box : f->client_bboxes){
                // client->edge_logger->logger->info("start2 to write file: {}", box.class_name);
                if(each_class_res.find(box.class_name) == each_class_res.end()){
                    //create file
                    auto class_file = exp_dir / fmt::format("{}.txt", box.class_name);
                    client->edge_logger->logger->info("start2 to write file: {}", class_file.string());
                    FILE* class_handler = fopen(class_file.c_str(), "w+");
                    each_class_res[box.class_name] = class_handler;
                }
                auto file_handler = each_class_res[box.class_name];
                string c = fmt::format("{0} {1} {2} {3} {4} {5}\n", f->frame_idx, box.confidence, box.xmin, box.ymin, box.xmax, box.ymax);
                fwrite(c.data(), sizeof(char), c.length(), file_handler);
            }
        }
    }
    fclose(imgSet_handler);
    for(auto kv : each_class_res){
        fclose(kv.second);
    }
}

void EdgeFramePool::export_client_boxes()
{
    // load all client boxes to log file.
    auto exp_dir = this->app->get_file_path(path(app->config["exp_dir"].Scalar()));
    
    if(!exists(exp_dir)){
        create_directory(exp_dir);
    }
    auto file_str = exp_dir / "client_boxes.log";
    const char* file_str_time = file_str.c_str();
    printf("write to %s\n", file_str_time);

    FILE *log_handler = fopen(file_str_time, "w+");
    for (int i = 0; i < frames.size(); i++)
    {
        int frame_idx = frames[i]->frame_idx;
        // cv::Mat temp =  frames[i]->raw_frame;
        vector<EdgeBox> client_bboxes = frames[i]->client_bboxes;
        if (client_bboxes.size() != 0)
        {
            for (int j = 0; j < client_bboxes.size(); j++)
            {
                EdgeBox bbox = client_bboxes[j];
                float xmin = bbox.xmin;
                float xmax = bbox.xmax;
                float ymin = bbox.ymin;
                float ymax = bbox.ymax;
                int track_id = bbox.track_id;
                string class_name = bbox.class_name;
                float confidence = bbox.confidence;
                // rectangle(temp, cv::Point(xmin, ymin), cv::Point(xmax, ymax), cv::Scalar(0, 255, 255), 2, 8);
                char content[256];
                sprintf(content, "%d %s %f %f %f %f %f\n", frame_idx, class_name.c_str(), confidence, xmin, xmax, ymin, ymax);
                fwrite(content, sizeof(char), strlen(content), log_handler);
                fflush(log_handler);
            }

            // char filename[256];
            // int num_from_middle_to_choose = std::stoi(app->config["client"]["tracker"]["opencv_tracker"]["num_from_middle_to_choose"].Scalar());
            // sprintf(filename, "data/jpg-%d/%d.jpg", num_from_middle_to_choose, frame_idx);
            // imwrite(filename,temp);
        }
    }
    fclose(log_handler);
}

void EdgeFramePool::export_rendered_images() {
    if (this->app->config["client"]["control"]["free_mat"].Scalar() == "true") {
        this->app->edge_logger->logger->error("cannot render images for mat is released");
        return;
    }
    auto exp_dir = path(app->config["client"]["control"]["exp_dir"].Scalar());
    if (!exists(exp_dir)) {
        create_directory(exp_dir);
    }
    for (int i = 0; i < frames.size(); i++) {
        int frame_idx = frames[i]->frame_idx;
        if (frame_idx < 0) break;
        cv::Mat image = frames[i]->raw_frame;
        vector <EdgeBox> client_bboxes = frames[i]->client_bboxes;
        for (int j = 0; j < client_bboxes.size(); j++) {
            EdgeBox bbox = client_bboxes[j];
            float xmin = bbox.xmin;
            float xmax = bbox.xmax;
            float ymin = bbox.ymin;
            float ymax = bbox.ymax;
            cv::Point originalPoint = cv::Point(xmin, ymin);
            cv::Point processPoint = cv::Point(xmax, ymax);
            int track_id = bbox.track_id;
            string class_name = bbox.class_name;
            cv::rectangle(image, originalPoint, processPoint, cv::Scalar(255, 0, 0), 2);
            // cv::putText(image, class_name, originalPoint,cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(255,0,0), 2);
        }
//        if (client_bboxes.size() == 0 && frames[i]->refer_frame_idx != -1)
//        {
//            vector<EdgeBox> server_bbox = frames[(frames[i]->refer_frame_idx)]->server_bboxes;
//            for (int j = 0; j < server_bbox.size(); j++)
//            {
//                EdgeBox bbox = server_bbox[j];
//                float xmin = bbox.xmin;
//                float xmax = bbox.xmax;
//                float ymin = bbox.ymin;
//                float ymax = bbox.ymax;
//                cv::Point originalPoint = cv::Point(xmin, ymin);
//                cv::Point processPoint = cv::Point(xmax, ymax);
//                int track_id = bbox.track_id;
//                string class_name = bbox.class_name;
//                cv::rectangle(image, originalPoint, processPoint, cv::Scalar(0, 0, 255), 1);
//                // cv::putText(image, class_name, originalPoint,cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(255,0,0), 2);
//            }
//        }
//        if(frames[i]->refer_frame_idx>=0) {
//            vector<EdgeBox> gt_bbox = frames[i]->gt_bboxes;
//            for (int j = 0; j < gt_bbox.size(); j++) {
//                EdgeBox bbox = gt_bbox[j];
//                float xmin = bbox.xmin;
//                float xmax = bbox.xmax;
//                float ymin = bbox.ymin;
//                float ymax = bbox.ymax;
//                cv::Point originalPoint = cv::Point(xmin, ymin);
//                cv::Point processPoint = cv::Point(xmax, ymax);
//                int track_id = bbox.track_id;
//                string class_name = bbox.class_name;
//                cv::rectangle(image, originalPoint, processPoint, cv::Scalar(0, 255, 0), 2);
//                // cv::putText(image, class_name, originalPoint,cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(0,255,0), 2);
//            }
//        }
        EdgeClient *client = (EdgeClient *) app;
        client->edge_logger->logger->info(fmt::format("write img to {}", "data/jpg/" + to_string(frame_idx) + ".jpg"));
        auto save_jpg_path = exp_dir / fmt::format("{}.jpg", frame_idx);
        cv::imwrite(save_jpg_path.string(), image);
    }
}
void EdgeFramePool::export_tracking_boxes_to_xml(){
    EdgeClient* client = (EdgeClient*) app;
    auto exp_dir = this->app->get_file_path(path(app->config["exp_dir"].Scalar()));
    client->edge_logger->logger->info("writing to exp_dir:{}", exp_dir.string());
    if(!exists(exp_dir)){
        client->edge_logger->logger->info("try to create exp_dir:{}", exp_dir.string());
        create_directory(exp_dir);
        client->edge_logger->logger->info("success to create exp_dir:{}", exp_dir.string());
    }
    auto xml_dir =  exp_dir / "client_boxes";
    client->edge_logger->logger->info("writing to xml_dir:{}", xml_dir.string());
    if(!exists(xml_dir)){
        client->edge_logger->logger->info("try to create xml_dir:{}", xml_dir.string());
        create_directory(xml_dir);
        client->edge_logger->logger->info("success to create xml_dir:{}", xml_dir.string());
    }
    DeleteFile(xml_dir.string().c_str());
    


    for(auto f : frames){
        if(f->frame_idx < 0) continue;
        pugi::xml_document doc;
        pugi::xml_node annotation_node = doc.append_child("annotation");
        // 分别存入每个box
        if(f->client_bboxes.size()>0){
            string content = fmt::format("{:06d}.xml", f->frame_idx);
            auto content_path = xml_dir / content;

            for(auto box : f->client_bboxes){
                pugi::xml_node object_node = annotation_node.append_child("object");
                pugi::xml_node trackid_node= object_node.append_child("trackid");
                trackid_node.append_child(pugi::node_pcdata).set_value((to_string(box.track_id).c_str()));
                pugi::xml_node name_node= object_node.append_child("name");
                name_node.append_child(pugi::node_pcdata).set_value((box.class_name.c_str()));
                pugi::xml_node confidence_node= object_node.append_child("confidence");
                confidence_node.append_child(pugi::node_pcdata).set_value((to_string(box.confidence).c_str()));
                pugi::xml_node bndbox_node= object_node.append_child("bndbox");
                pugi::xml_node xmin_node= bndbox_node.append_child("xmin");
                xmin_node.append_child(pugi::node_pcdata).set_value((to_string(box.xmin).c_str()));
                pugi::xml_node xmax_node= bndbox_node.append_child("xmax");
                xmax_node.append_child(pugi::node_pcdata).set_value((to_string(box.xmax).c_str()));
                pugi::xml_node ymin_node= bndbox_node.append_child("ymin");
                ymin_node.append_child(pugi::node_pcdata).set_value((to_string(box.ymin).c_str()));
                pugi::xml_node ymax_node= bndbox_node.append_child("ymax");
                ymax_node.append_child(pugi::node_pcdata).set_value((to_string(box.ymax).c_str()));
                doc.save_file(content_path.c_str());
            }
        }
    }
}
void EdgeFramePool::export_read_timestamps(){
    auto exp_dir = this->app->get_file_path(path(app->config["exp_dir"].Scalar()));
    
    if(!exists(exp_dir)){
        create_directory(exp_dir);
    }
    auto read_timestamps_file = exp_dir / "read_timestamps.txt";
    
    FILE* read_timestamps_handler = fopen(read_timestamps_file.c_str(), "w+");
    map<int, long long>::iterator iter;
    iter = read_frame_timestamps.begin();
    while(iter != read_frame_timestamps.end()) {
        string c = fmt::format("{0} {1}\n", iter->first, iter->second);
        fwrite(c.data(), sizeof(char), c.length(), read_timestamps_handler);
        iter++;
    }


    fclose(read_timestamps_handler);
}
void EdgeFramePool::export_recv_timestamps(){
    auto exp_dir = this->app->get_file_path(path(app->config["exp_dir"].Scalar()));
    
    if(!exists(exp_dir)){
        create_directory(exp_dir);
    }
    auto recv_timestamps_file = exp_dir / "recv_timestamps.txt";
    auto local_detect_timestamps_file = exp_dir / "local_detect_timestamps.txt";

    int total_box_num = 0;
    long long total_latency = 0;
    int edge_box_num = 0;
    long long edge_latency = 0;
    int local_box_num = 0;
    long long local_latency = 0;
    FILE* recv_timestamps_handler = fopen(recv_timestamps_file.c_str(), "w+");
    FILE* local_detect_timestamps_handler = fopen(local_detect_timestamps_file.c_str(), "w+");
    map<int, map<int, pair<long long, vector<EdgeBox>>>>::iterator iter;
    iter = recv_frame_timestamps.begin();
    while(iter != recv_frame_timestamps.end()) {
        int frame_id = iter->first;
        map<int, pair<long long, vector<EdgeBox>>>::iterator iter2;
        iter2 = iter->second.begin();
        while(iter2!=iter->second.end()){
            long long timestamp = iter2->second.first;
            vector<EdgeBox> boxes = iter2->second.second;
            int boxes_size = boxes.size();
            
            int latency = timestamp - read_frame_timestamps[frame_id];
            total_latency = total_latency + latency * boxes_size;
            total_box_num = total_box_num + boxes_size;
            edge_latency = edge_latency + latency * boxes_size;
            edge_box_num = edge_box_num + boxes_size;
            for (int i = 0; i < boxes.size(); i++){
                // int xmin = boxes[i].xmin;
                string c = fmt::format("{0} {1} {2} {3} {4} {5} {6} {7}\n", frame_id, iter2->first, timestamp, latency, boxes[i].xmin, boxes[i].ymin, boxes[i].xmax, boxes[i].ymax);
                fwrite(c.data(), sizeof(char), c.length(), recv_timestamps_handler);
            }


            iter2++;
        }
        
        iter++;
    }
    map<int, map<int, pair<long long, vector<EdgeBox>>>>::iterator iter3;
    iter3 = valid_local_finish_frame_timestamps.begin();
    while(iter3!=valid_local_finish_frame_timestamps.end()){
        int frame_id = iter3->first;
        map<int, pair<long long, vector<EdgeBox>>>::iterator iter4;
        iter4 = iter3->second.begin();
        while(iter4!=iter3->second.end()){
            long long timestamp = iter4->second.first;
            vector<EdgeBox> boxes = iter4->second.second;
            int boxes_size = boxes.size();
            int latency = timestamp - read_frame_timestamps[frame_id];
            total_latency = total_latency + latency * boxes_size;
            total_box_num = total_box_num + boxes_size;
            local_latency = local_latency + latency * boxes_size;
            local_box_num = local_box_num + boxes_size;
            for (int i = 0; i < boxes.size(); i++){
                string c = fmt::format("{0} {1} {2} {3} {4} {5} {6} {7}\n", frame_id, iter4->first, timestamp, latency, boxes[i].xmin, boxes[i].ymin, boxes[i].xmax, boxes[i].ymax);
                fwrite(c.data(), sizeof(char), c.length(), local_detect_timestamps_handler);
            }

            iter4++;
        }
        iter3++;
    }
    
    fclose(recv_timestamps_handler);
    fclose(local_detect_timestamps_handler);
    double average_object_latency = total_latency * 1.0/ total_box_num;
    double average_edge_latency = edge_latency * 1.0 / edge_box_num;
    double average_local_latency = local_latency * 1.0 / local_box_num;
    printf("total latency: %lldms\n", total_latency);
    printf("total object number: %d\n", total_box_num);
    printf("average object latency: %.4fms\n",average_object_latency);
    printf("edge latency: %lldms\n", edge_latency);
    printf("edge object number: %d\n", edge_box_num);
    printf("average edge object latency: %.4fms\n",average_edge_latency);
    printf("local latency: %lldms\n", local_latency);
    printf("local object number: %d\n", local_box_num);
    printf("average local object latency: %.4fms\n",average_local_latency);

    
}