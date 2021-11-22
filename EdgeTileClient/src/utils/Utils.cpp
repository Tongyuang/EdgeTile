//
// Created by Xu Wang on 2019/12/13.
//

#include "Utils.hpp"
#include "../log/EdgeLog.hpp"
#include <arpa/inet.h>
#include <iostream>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace Edge;

YAML::Node Utils::load_config(std::string &file_path) {
    return YAML::LoadFile(file_path);
}

void Utils::init_log(std::string log_path) {
    auto logger = EdgeLog("Client", log_path);
    logger.logger->info("hello world");
    auto child_logger = logger.getChild("Socket");
    child_logger->logger->info("socket start");
}

long long Utils::current_time() {
    std::chrono::milliseconds ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch());
    return ms.count();
}

int Utils::convert_big2small(int32_t bigEndianValue) {
    uint8_t myByteArray[4];
    memcpy(&bigEndianValue, myByteArray, sizeof(bigEndianValue));
    return ntohl(bigEndianValue);
}

double Utils::getPSNR(cv::Mat& I1, cv::Mat& I2)
{
    cv::Mat s1;
    absdiff(I1, I2, s1);       // |I1 - I2|
    s1.convertTo(s1, CV_32F);  // cannot make a square on 8 bits
    s1 = s1.mul(s1);           // |I1 - I2|^2

    cv::Scalar s = sum(s1);         // sum elements per channel
    s1.release();

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    if(sse <= 1e-10) // for small values return zero
        return 0;
    else
    {
        double  mse =sse /(double)(I1.channels() * I1.total());
        double psnr = 10.0*log10((255*255)/mse);
        return psnr;
    }
}
// 计算SSIM
cv::Scalar Utils::getMSSIM(const cv::Mat& i1, const cv::Mat& i2)
{
    const double C1 = 6.5025, C2 = 58.5225;
    /***************************** INITS **********************************/
    int d     = CV_32F;

    cv::Mat I1, I2;
    i1.convertTo(I1, d);           // 不能在单字节像素上进行计算，范围不够。
    i2.convertTo(I2, d);

    cv::Mat I2_2   = I2.mul(I2);        // I2^2
    cv::Mat I1_2   = I1.mul(I1);        // I1^2
    cv::Mat I1_I2  = I1.mul(I2);        // I1 * I2

    /***********************初步计算 ******************************/

    cv::Mat mu1, mu2;   //
    cv::GaussianBlur(I1, mu1,cv::Size(11, 11), 1.5);
    cv::GaussianBlur(I2, mu2, cv::Size(11, 11), 1.5);

    cv::Mat mu1_2   =   mu1.mul(mu1);
    cv::Mat mu2_2   =   mu2.mul(mu2);
    cv::Mat mu1_mu2 =   mu1.mul(mu2);

    cv::Mat sigma1_2, sigma2_2, sigma12;

    cv::GaussianBlur(I1_2, sigma1_2, cv::Size(11, 11), 1.5);
    sigma1_2 -= mu1_2;

    cv::GaussianBlur(I2_2, sigma2_2, cv::Size(11, 11), 1.5);
    sigma2_2 -= mu2_2;

    cv::GaussianBlur(I1_I2, sigma12, cv::Size(11, 11), 1.5);
    sigma12 -= mu1_mu2;

    ///////////////////////////////// 公式 ////////////////////////////////
    cv::Mat t1, t2, t3;

    t1 = 2 * mu1_mu2 + C1;
    t2 = 2 * sigma12 + C2;
    t3 = t1.mul(t2);              // t3 = ((2*mu1_mu2 + C1).*(2*sigma12 + C2))

    t1 = mu1_2 + mu2_2 + C1;
    t2 = sigma1_2 + sigma2_2 + C2;
    t1 = t1.mul(t2);               // t1 =((mu1_2 + mu2_2 + C1).*(sigma1_2 + sigma2_2 + C2))

    cv::Mat ssim_map;
    cv::divide(t3, t1, ssim_map);      // ssim_map =  t3./t1;

    cv::Scalar mssim = cv::mean( ssim_map ); // mssim = ssim_map的平均值
    return mssim;
}

int Utils::getDiff(cv::Mat a, cv::Mat b){
    // a, b grey
    cv::Mat diff;
    cv::Mat comp;
    cv::absdiff(a, b, diff);
    // cout << "diff" << endl << diff << endl << endl;

    // if pixel difference > 35, is seen as different. (Page 5 in paper.)
    cv::compare(diff, cv::Scalar(35), comp, cv::CMP_GE);
    cv::Mat one(a.rows, a.cols, a.type(), cv::Scalar(1));
    cv::Mat compOne;
    cv::bitwise_and(comp, one, compOne);
    cv::Scalar result = cv::sum(compOne);
    // cout << "comp" << endl << cv::format(compOne, cv::Formatter::FMT_NUMPY)  << endl << endl;
    // printf("result:%d\n",(int)result[0]);
    // getchar();
    return (int)result[0];
}
double Utils::calculateSD(std::vector<double> numArray){
    double sum = 0.0, standardDeviation = 0.0;
    int length = numArray.size();
    for(double num : numArray) {
        sum += num;
    }
    double mean = sum/length;
    for(double num: numArray) {
        standardDeviation += std::pow(num - mean, 2);
    }
    return std::sqrt(standardDeviation/length);
}

int Utils::Max(int a, int b)
{
    if (a > b)
        return a;
    return b;
}


vector<size_t> Utils::sort_indexes(const vector<int> &v) {

    // initialize original index locations
    vector<size_t> idx(v.size());
    iota(idx.begin(), idx.end(), 0);

    // sort indexes based on comparing values in v
    // using std::stable_sort instead of std::sort
    // to avoid unnecessary index re-orderings
    // when v contains elements of equal values
    stable_sort(idx.begin(), idx.end(),
                [&v](size_t i1, size_t i2) {return v[i1] < v[i2];});

    return idx;
}