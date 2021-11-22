//
// Created by Xu Wang on 2019/12/16.
//

#ifndef EDGETILECPP_EDGEFRAME_HPP
#define EDGETILECPP_EDGEFRAME_HPP
#include <opencv2/opencv.hpp>
#include <string>
#include "EdgeBox.hpp"
#include "../utils/EdgeGroupPolicy.hpp"
#include "EdgePacket.hpp"
using namespace std;

namespace Edge {
    class EdgeFrame: public EdgePacket {
    public:
        EdgeFrame();
        cv::Mat raw_frame;

        cv::Mat yuv_data;
        vector<cv::Mat> yuv_frame;
        EdgeGroupPolicy groupPolicy;
        int frame_idx;
        string video_path;
        int w;
        int h;
        int m_diff;

        vector<EdgeBox> gt_bboxes;

        vector<EdgeBox> client_bboxes;

        vector<EdgeBox> local_bboxes;
        vector<EdgeBox> local_detect_bboxes;
        vector<map<string, int>> motion_vectors;

        vector<EdgeBox> merged_bboxes;

        bool will_upload;
        bool in_blacklist;

        bool is_server_key_frame;
        bool is_local_key_frame;

        bool is_track_finished;
        void convert_rgb2yuv();
        void load_bboxes(string file_path, shared_ptr<EdgeFrame> f, int zoom_scale, int track_features);
        void load_bboxes(string file_path, string file_path2);
        void load_motionVectors(string file_path);
        void load_local_detect_bboxes(string file_path);
        vector<EdgeBox> diff_local_bboxes(vector<EdgeBox> boxes, double thres);
        cv::Mat render();
        // record time
        double before_encoding_time;
        double before_tracking_time;
        double before_render_time;
    };
}

#endif //EDGETILECPP_EDGEFRAME_HPP
