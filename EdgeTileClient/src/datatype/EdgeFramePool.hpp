//
// Created by Xu Wang on 2020/5/30.
//

#ifndef EDGETILECPP_EDGEFRAMEPOOL_HPP
#define EDGETILECPP_EDGEFRAMEPOOL_HPP

#include "EdgePacket.hpp"
#include "EdgeVideo.hpp"
#include "EdgeFrame.hpp"

using namespace std;
namespace Edge {
    class EdgeApp;
    class EdgeFramePool : public EdgePacket{
    public:
        EdgeFramePool(EdgeApp *app);
        shared_ptr<EdgeVideo> videoAttrs; //video
        vector <shared_ptr<EdgeFrame>> frames;// frame
        map<int, long long> read_frame_timestamps; // 记录所有的时间戳

        // 这个里面只存来自服务器的box：
        map<int, map<int, pair<long long, vector<EdgeBox>>>> recv_frame_timestamps; 

        map<int,  pair<long long, vector<EdgeBox>>> local_finish_frame_timestamps;

        // 这个里面只存来自本地的box：
        map<int,  map<int, pair<long long, vector<EdgeBox>>>> valid_local_finish_frame_timestamps;
        
        map<int, vector<EdgeBox>> local_detect_boxes;
        EdgeApp *app;

        int last_free_frame;


    public:
        void export_rendered_images();

        void export_client_boxes();

        void export_tracking_boxes();

        void export_tracking_boxes_to_xml();
        void export_read_timestamps();
        void export_recv_timestamps();

        double calculate_fps(int last_frame);

        void cal_precision();


    };
}


#endif //EDGETILECPP_EDGEFRAMEPOOL_HPP
