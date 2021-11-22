/*
 * @Author: Xu Wang
 * @Date: Sunday, November 17th 2019
 * @Email: wangxu.93@hotmail.com
 * @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
 */
#ifndef KVAZAAR_ENCODER_H
#define KVAZAAR_ENCODER_H
#include "kvazaar.h"
#include <stdio.h>
#include <vector>
#include <sys/socket.h>
#include <mutex>
#include "Semaphore.hpp"
#include <opencv2/core.hpp>

namespace cv {
namespace kvazaar_encoder{

class CV_EXPORTS_W_SIMPLE EncoderResult{
public:
    CV_PROP_RW int encoderState;
    CV_PROP_RW int frameRead;
    CV_PROP_RW int frameWrite;
};

enum EncodeMode {
    UNSET_MODE=0,
    LOCAL_FILE_MODE=1,
    SERVER_MODE=2
};

class CV_EXPORTS_W KvazaarEncoder
{
public:
    CV_WRAP KvazaarEncoder(String&fileName){videoName = fileName;}
    virtual ~KvazaarEncoder() {}
     CV_WRAP bool start(int width, int height, int gopSize, String& tile_split, int nthreads, String& quality);
     CV_WRAP static bool setFileMode(String& filename);
     CV_WRAP static bool setServerMode(String& server_addr, int port);
     CV_WRAP EncoderResult encode(InputArray y, InputArray u, InputArray v, int frame_idx);
     CV_WRAP void stop();
     CV_WRAP int getEncodeStatus();
     CV_WRAP int setEncodingPriority(String& priority);
    
  
public:
    static const kvz_api *kvz_api_instance;
    static std::mutex* writeDataLock;
    static FILE** outputHandlers;
    static void (*writeDataCallbackPtr)(int, uint8_t *, int);
    static void write_data_to_file(int frame_id, int tile_id, u_int8_t *data, int len);
    static void write_data_to_sock(int frame_id, int tile_id, u_int8_t *data, int len);

private:
    kvz_encoder *kvz_encoder_instance;
    kvz_config *kvz_config_instance;
    int frameEncodeNum;
    int frameReadNum;
    kvz_picture *inRawFrame;
    std::mutex rawFrameLock;
    Semaphore* rawFrameSemaphore;
    int encodeStatus;
    static EncodeMode mode;
    static String filePrefix;
    static String serverAddr;
    static int serverPort;
    static int sock;
    static int tileCount;
    static int tileWidth;
    static int tileHeight;
    static int videoWidth;
    static int videoHeight;
    static String videoName;
    static bool hasSendVideoHeader;
    
    void initStatus();
    
    bool open(int width, int height, int gopSize, const char* tile_split, int nthreads, const char* quality);
    
    static void* run(void* context);
    static FILE* logHandler;
    static void writeData(int frame_id, int tile_id, void *chunk_data);
    kvz_picture* alloc_pic();
};

}
}





#endif
