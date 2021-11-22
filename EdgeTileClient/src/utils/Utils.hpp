//
// Created by Xu Wang on 2019/12/13.
//

#ifndef EDGETILECPP_UTILS_HPP
#define EDGETILECPP_UTILS_HPP

#include <string>
#include "yaml-cpp/yaml.h"
#include "spdlog/spdlog.h"

#include "opencv2/opencv.hpp"
#include "opencv2/imgcodecs.hpp"
#include "../datatype/EdgeBox.hpp"
namespace Edge {

    class Utils {
    public:
        static YAML::Node load_config(std::string& file_path);
        static void init_log(std::string log_path);
        static long long current_time();
        static int convert_big2small(int32_t v);
        static cv::Scalar getMSSIM(const cv::Mat& i1, const cv::Mat& i2);
        static double getPSNR(cv::Mat& I1, cv::Mat& I2);
        static int getDiff(cv::Mat a, cv::Mat b);
        static double calculateSD(std::vector<double> numArray);
        static int Max(int a, int b);

        static vector<size_t> sort_indexes(const vector<int> &v);
    };
}


#endif 
//EDGETILECPP_UTILS_HPP
