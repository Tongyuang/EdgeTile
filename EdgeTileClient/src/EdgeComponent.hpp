//
// Created by Xu Wang on 2019/12/15.
//

#ifndef EDGETILECPP_EDGECOMPONENT_HPP
#define EDGETILECPP_EDGECOMPONENT_HPP
#include <pthread.h>
#include <string>
#include "log/EdgeLog.hpp"
#include "yaml-cpp/yaml.h"
#include <pthread.h>
#include "datatype/EdgePacket.hpp"
#include "utils/EdgeQueue.hpp"

namespace Edge {
    class EdgeApp;

    enum  Pthread_Status{
        PTHREAD_NOT_START=0,
        PTHREAD_RUN=1,
        PTHREAD_EXIT=2
    };

    class EdgeComponent {
    public:
        EdgeComponent(EdgeApp* app, std::string component_name);
        void start();
        void init();
        void stop();
        void join();
        bool is_init();
        bool is_stopped();
        void yield(std::shared_ptr<EdgePacket> packet);
        virtual void run()=0;
        virtual void initialize()=0;


    public:
        EdgeApp* app;
        YAML::Node config;
        std::string component_name;
        EdgeLog* edge_logger;
        EdgeQueue dataQueue;
    private:
        pthread_t tid;
        bool  init_status;
        Pthread_Status thread_status;
        static void* run_func(void* context);
    };
}


#endif //EDGETILECPP_EDGECOMPONENT_HPP
