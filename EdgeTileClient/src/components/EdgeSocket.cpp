//
// Created by Xu Wang on 2019/12/15.
//
#include <string>
#include <exception>
#include "EdgeSocket.hpp"
#include "../EdgeApp.hpp"
#include "../utils/Utils.hpp"
#include "../include/EdgeClient.hpp"

using namespace Edge;
using namespace std;

EdgeSocket::EdgeSocket(EdgeApp *app) : EdgeComponent(app, "socket") {

}

void EdgeSocket::initialize() {
    string ip_addr = config["ip_addr"].Scalar();
    int port = stoi(config["port"].Scalar());
    edge_logger->logger->info(fmt::format("Connect to server:{0} port:{1}", ip_addr, port));
    try {
        if (!conn.connect(sockpp::inet_address(ip_addr, port))) {
            edge_logger->logger->error("connect to server failed");
        }
    } catch (exception e) {
        edge_logger->logger->error(fmt::format("error in socket initialize: {0}", e.what()));
    }
}

void EdgeSocket::run() {
    try {
        while (!is_stopped()) {
            json box = recv();

            if (box.empty() == true) {
                // EdgeClient* client = (EdgeClient*)(this->app);
                // client->get_framePool()->export_read_timestamps();
                // client->get_framePool()->export_recv_timestamps();
                edge_logger->logger->error("socket exit...");
                break;
            }
            //EdgeClient *client = (EdgeClient *) app;
            //vector<EdgeBox> recv_boxes;

            int frame_id = box["frame_id"];
            string level = box["level"];
            int group_id = box["group_id"];
            shared_ptr<EdgeBoxArray> boxArray = shared_ptr<EdgeBoxArray>(new EdgeBoxArray());
            auto bboxs = box["boxes"];
            for (json::iterator it = bboxs.begin(); it != bboxs.end(); ++it)
            {
                EdgeBox b(*it);
                b.is_server = true;
                boxArray->boxes.push_back(b);
            }
            boxArray->frame_id = frame_id;
            boxArray->group_id = group_id;
            boxArray->level = level;

            edge_logger->logger->info(
                    fmt::format("recv frame detect result from server: {0}", frame_id));
            // 记录获取到返回结果的时间
            EdgeClient* client = (EdgeClient*)(this->app);
            if (client->get_framePool()->recv_frame_timestamps.find(frame_id) == client->get_framePool()->recv_frame_timestamps.end()) {
                client->get_framePool()->recv_frame_timestamps[frame_id] = map<int, pair<long long, vector<EdgeBox>>>();
            }
            client->get_framePool()->recv_frame_timestamps[frame_id][group_id].first = Utils::current_time();
            // 筛选掉本地检测的box
            float iou_thres = 0.3;
            int valid_box_num = boxArray->boxes.size();
            vector<EdgeBox> valid_boxes;
            // 调用local_detect_boxes这个map的find函数，find函数返回end说明没找到，进而说明这个frame没有被local detector预测过
            if(client->get_framePool()->local_detect_boxes.find(frame_id)!=client->get_framePool()->local_detect_boxes.end()){
                int local_box = 0;
                vector<EdgeBox> valid_local_boxes;

                // 这里判断的是local_detect_boxes里面这个frame对应的box大小
                if(client->get_framePool()->local_detect_boxes[frame_id].size() != 0){

                    // 遍历boxArray里面的每个box（本质上是遍历传回来的那个group的检测结果所有的box）
                    for(int i = 0; i < boxArray->boxes.size(); i++){
                        int flag = false;
                        // 对于每个传回来的box，遍历local的所有box，找一下哪些iou可行
                        for(int j = 0; j < client->get_framePool()->local_detect_boxes[frame_id].size(); j++){
                            float iou = boxArray->boxes[i].calculate_iou(client->get_framePool()->local_detect_boxes[frame_id][j]);
                            if(iou >= iou_thres){
                                flag = true;
                                valid_box_num -= 1; // 少一个valid box
                                local_box += 1; // 多一个本地box
                                valid_local_boxes.push_back(client->get_framePool()->local_detect_boxes[frame_id][j]);
                            }
                        }
                        if (flag == false){ //遍历完所有的local box，发现没有一个iou比较高的，只能用服务器侧的了，于是更新valid_box
                            valid_boxes.push_back(boxArray->boxes[i]);
                        }
                    }
                }else{
                    valid_boxes = boxArray->boxes;
                }

                // 更新
                if(client->get_framePool()->valid_local_finish_frame_timestamps.find(frame_id) == client->get_framePool()->valid_local_finish_frame_timestamps.end()){
                    client->get_framePool()->valid_local_finish_frame_timestamps[frame_id] = map<int, pair<long long, vector<EdgeBox>>>();
                }
                client->get_framePool()->valid_local_finish_frame_timestamps[frame_id][group_id].first = client->get_framePool()->local_finish_frame_timestamps[frame_id].first;
                client->get_framePool()->valid_local_finish_frame_timestamps[frame_id][group_id].second = valid_local_boxes;
            }else{
                valid_boxes = boxArray->boxes;
                printf("local not detect yet...\n");
            }

            // 在这里更新client侧的只来自服务器的box
            client->get_framePool()->recv_frame_timestamps[frame_id][group_id].second = valid_boxes;
            
            // yield函数，这里boxArray 从server来，调用update_reference_box函数更新tracker
            yield(boxArray);
            edge_logger->logger->info(
                    fmt::format("*bbox_recv frame: {0} level: {1} group: {2} box number: {3} filtered number:{4}", frame_id, level, group_id, boxArray->boxes.size(), valid_box_num));
        }
        conn.close();
    } catch (exception e) {
        edge_logger->logger->error(fmt::format("error in socket recv: {0}", e.what()));
    }
    edge_logger->logger->error("socket thread exit...");
}

void EdgeSocket::shutdown() {
    conn.shutdown();
}

json EdgeSocket::recv() {
    try {
        int msg_size = 4;
        int msg_len = 0;

        conn.read_n(&msg_len, 4);
        msg_len = ntohl(msg_len);
        char *buf = new char[msg_len + 1];
        memset(buf, 0, sizeof(char) * (msg_len + 1));
        conn.read_n(buf, msg_len);
        auto recv_bbox = json::parse(buf);
        return recv_bbox;
    } catch (exception e) {
        edge_logger->logger->error(fmt::format("error happend in recv:{0}", e.what()));
        return json();
    }


}

