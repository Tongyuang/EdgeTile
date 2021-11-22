//
// Created by Xu Wang on 2019/12/15.
//

#ifndef EDGETILECPP_EDGEENCODER_HPP
#define EDGETILECPP_EDGEENCODER_HPP

#include <opencv2/KvazaarEncoder.hpp>
#include <opencv2/opencv.hpp>
#include "../EdgeComponent.hpp"
#include "../utils/EdgeQueue.hpp"
#include "../utils/EdgeGroupPolicy.hpp"
#include "../datatype/EdgeVideo.hpp"

using namespace cv;

namespace Edge {

    class EdgeApp;

    class EdgeEncoder : public EdgeComponent {
    public:
        explicit EdgeEncoder(EdgeApp *app);

        ~EdgeEncoder() { delete encoder; }

        void run() override;

        void initialize() override;

        void HEVCEncode(string video_name);

        void JPEGEncode(string video_name);

        void FakeEncode(string video_name);

        int tile_width;

        int tile_height;

        vector<Rect> tiles_position;

        EdgeGroupPolicy currentPolicy;

        map<int, map<int, uint8_t *>> hevc_data;

        map<int, map<int, int>> meta_data;
        map<int, vector<int>> upload_order_data;

        int sock;

        float getFrameEncodingTile();

        shared_ptr<EdgeVideo> videoAttrs;

    private:
        cv::kvazaar_encoder::KvazaarEncoder *encoder;

        void calculate_tiles_position();
    };
}


#endif //EDGETILECPP_EDGEENCODER_HPP
