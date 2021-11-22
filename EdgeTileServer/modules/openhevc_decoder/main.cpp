//
//  main.cpp
//  HEVCDecoder
//
//  Created by Xu Wang on 2019/11/18.
//  Copyright © 2019 Xu Wang. All rights reserved.
//

#include "OpenHEVCDecoder.hpp"
#include <opencv2/imgproc.hpp>
#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>


int main(int argc, const char * argv[]) {
    cv::openhevc_decoder::OpenHEVCDecoder decoder;
    decoder.start(8080);
    cv::openhevc_decoder::FrameTile f;
    while(1){
        f = decoder.read();
        if(f.frame_id<0)
        {
            break;
        }
        char filename[256];
        sprintf(filename, "%s_frame_%d_tile_%d.jpg", "test", f.frame_id, f.tile_id);
        imwrite(filename, f.rawImage);
    };
    fprintf(stdout, "finish!");

}
