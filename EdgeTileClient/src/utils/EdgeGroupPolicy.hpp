//
// Created by Xu Wang on 2020/4/10.
//

#ifndef EDGETILECPP_EDGEGROUPPOLICY_HPP
#define EDGETILECPP_EDGEGROUPPOLICY_HPP

#include <opencv2/core.hpp>
#include <vector>

using namespace cv;
using namespace std;
namespace Edge {
    class EdgeEncoder;

    struct TileMeta {
        int tile_id;
        int group_id;
        int group_width;
        int group_height;
    };

    class EdgeGroupPolicy {
    public:
        EdgeGroupPolicy(EdgeEncoder *encoder);

        EdgeGroupPolicy();

        vector<cv::Rect> groups;

        EdgeEncoder *encoder;

        static void default_policy(int tw, int th, EdgeGroupPolicy &policy);

        static void one_group_policy(int tw, int th, EdgeGroupPolicy &policy);

        cv::Rect group2box(int group_id);

        string toString();

        vector<TileMeta> getTileEncodingOrder(int tw, int th);

        EdgeGroupPolicy dynamic_by_count();
        EdgeGroupPolicy dynamic_by_object_nums(int frame_id, vector<int> upload_order);

    };
}


#endif //EDGETILECPP_EDGEGROUPPOLICY_HPP
