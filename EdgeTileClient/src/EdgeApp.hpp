//
// Created by Xu Wang on 2019/12/15.
//

#ifndef EDGETILECPP_EDGEAPP_HPP
#define EDGETILECPP_EDGEAPP_HPP

#include <string>
#include <map>
#include "yaml-cpp/yaml.h"
#include "log/EdgeLog.hpp"
#include "EdgeComponent.hpp"
#include <filesystem>

#if defined(__APPLE__)
#include "TargetConditionals.h"
#endif

using namespace std::__fs::filesystem;
using namespace std;

namespace Edge {

    class EdgeApp {
    public:


        //EdgeApp(std::string app_name,std::string logger_name,std::string config_path, std::string document_path, std::string exp_name, int work_mode, string group_policy, string video_name);

        EdgeApp(std::string app_name, std::string logger_name, std::string root_path, YAML::Node config);

        void register_component(std::string component_name, std::string component_class);

        void initialize();

        void start_components();

        EdgeComponent *get_components_by_name(std::string component_name);

        void stop();

        virtual void start() {}

        virtual void handle_yield(EdgeComponent* component, shared_ptr<EdgePacket> packet)=0;

        path get_file_path(string file_path);

    public:
        std::string app_name;
        //std::string document_path;
        path root_path;

        EdgeLog *edge_logger;

        YAML::Node config;
    private:
        std::map<std::string, EdgeComponent *> components;


    };
}


#endif //EDGETILECPP_EDGEAPP_HPP
