
#ifndef OpenHEVCDecoder_hpp
#define OpenHEVCDecoder_hpp

#include <stdio.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>
#include <vector>
#include <queue>
#include "openHevcWrapper.h"
#include <mutex>
#include <condition_variable>

namespace cv{
namespace openhevc_decoder{
enum DecoderStatus{
  DECODER_EXIT=0,
    DECODER_RUN=1
};
class Semaphore {
public:
  explicit Semaphore(int count = 0) : count_(count) {
  }

  void Signal() {
    std::unique_lock<std::mutex> lock(mutex_);
    ++count_;
    cv_.notify_one();
  }

  void Wait() {
    std::unique_lock<std::mutex> lock(mutex_);
    cv_.wait(lock, [=] { return count_ > 0; });
    --count_;
  }

private:
  std::mutex mutex_;
  std::condition_variable cv_;
  int count_;
};

class CV_EXPORTS_W_SIMPLE FrameTile{
public:
    CV_PROP_RW int frame_id;
    CV_PROP_RW int tile_id;
    CV_PROP_RW int groupId;
    CV_PROP_RW int groupSize;
    CV_PROP_RW Mat rawImage;
};

class CV_EXPORTS_W_SIMPLE VideoProperty{
  public:
    CV_PROP_RW int tile_width;
    CV_PROP_RW int tile_height;
    CV_PROP_RW int video_width;
    CV_PROP_RW int video_height;
    CV_PROP_RW String video_name;
};


class CV_EXPORTS_W OpenHEVCDecoder{
public:
    CV_WRAP OpenHEVCDecoder(){}
    CV_WRAP bool start(int port);
    CV_WRAP FrameTile read();
    CV_WRAP VideoProperty readVideoProperty();

private:
    
    String fileName;
    int port;
    VideoProperty videoProperty;
    int server_fd;
    int tile_count;
    DecoderStatus status;
    OpenHevc_Handle* handlers;
    
    std::queue<FrameTile*> decodedFrames;
    Semaphore* frameVectorSemaphore;
    Semaphore* videoPropertySemaphore;
    std::vector<OpenHevc_Frame> openHevcFrame;
    std::vector<OpenHevc_Frame_cpy> openHevcFrameCpy;
    std::vector<uint8_t*>yuv_buffer;
    std::mutex frameVectorLock;
    
    static void* run(void* context);
    static void* run_decode(void* context);
    int new_socket;
    std::vector<std::queue<int>> frame_id_list;
    std::vector<Rect> tiles_position;

    static void output_file(OpenHEVCDecoder* decoder, int frame_id, int tile_id, int group_id, int group_size, bool is_fake);

    FILE* logHandler;
    void calculate_tiles_position();
};

struct DecodeParams{
  OpenHEVCDecoder* decoder;
  uint8_t* buf;
  int buf_len;
  int tile_id;
  int group_id;
  int group_size;
};
}



}

#endif /* OpenHEVCDecoder_hpp */
