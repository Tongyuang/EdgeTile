//
// Created by Xu Wang on 2019/12/15.
//

#include "EdgeApp.hpp"
#include "spdlog/fmt/fmt.h"
#include "utils/Utils.hpp"
#include "components/EdgeEncoder.hpp"
#include "components/EdgeStreamer.hpp"
#include "components/EdgeSocket.hpp"
#include "components/EdgeTracker.hpp"
#include <map>

using namespace std;
using namespace Edge;

EdgeApp::EdgeApp(std::string app_name, std::string logger_name, std::string root_path, YAML::Node config){
    this->app_name = app_name;
    this->root_path = path(root_path);
    this->config = config[app_name];
    try {
        auto logger_dir = this->get_file_path(this->config["exp_dir"].Scalar());
        if(!exists(logger_dir)){
            create_directory(logger_dir);
        }
        this->edge_logger = new EdgeLog(logger_name, logger_dir);
    }catch (Exception& e){
        printf("errors occur when initializing edge log, please check file directory or config file data.\n");
    }
}


//EdgeApp::EdgeApp(std::string app_name,
//    std::string logger_name,
//    std::string config_path,
//    std::string root_path,
//    std::string exp_name,
//    int work_mode,
//    std::string group_policy, string video_name) {
//    this->app_name = app_name;
//    printf("init the app...\n");
//
//    this->root_path = path(root_path);
//    auto config_file =this->get_file_path(config_path).string();
//    //edge_logger->logger->info("loading config file from: {0}", config_file);
//    this->config = Utils::load_config(config_file);
//    // merge config
//    auto relative_exp_dir = path(config["client"]["control"]["exp_dir"].Scalar());
//    if(exp_name.length() > 0){
//        relative_exp_dir = relative_exp_dir.parent_path() / exp_name;
//        config["client"]["control"]["exp_dir"] = relative_exp_dir.string();
//    }
//    if(work_mode > 0){
//        if(work_mode == 1){
//            config["client"]["video_streamer"]["detector_mode"] = "server";
//        }
//        else if (work_mode == 2){
//            config["client"]["video_streamer"]["detector_mode"] = "local";
//        }
//        else if(work_mode==3){
//            config["client"]["video_streamer"]["detector_mode"] = "both";
//        }
//    }
//    if(group_policy.length()>0){
//        config["client"]["encoder"]["group_policy"] = group_policy;
//    }
//    if(video_name.length() > 0){
//        config["client"]["video_streamer"]["video_path"] = (path(config["client"]["video_streamer"]["video_path"].Scalar()).parent_path() / video_name).string();
//    }
//    auto exp_dir = this->get_file_path(relative_exp_dir);
//
//    if(!exists(exp_dir)){
//        create_directory(exp_dir);
//    }
//    auto logger_dir = this->get_file_path(config["client"]["control"]["exp_dir"].Scalar());
//    this->edge_logger = new EdgeLog(logger_name, logger_dir);
//}

void EdgeApp::register_component(std::string component_name, std::string component_class) {
    // do real register
    EdgeComponent *ec = NULL;
    map<string, int> components_dict = {
            {"EdgeEncoder",    0},
            {"EdgeStreamer",   1},
            {"EdgeController", 2},
            {"EdgeSocket",     3},
            {"EdgeTracker",    4}
    };
    int cid = -1;
    if (components_dict.count(component_class) > 0) {
        cid = components_dict[component_class];
    }
    switch (cid) {
        case 0: {
            ec = (EdgeComponent *) new EdgeEncoder(this);
            break;
        }
        case 1: {
            ec = (EdgeComponent *) new EdgeStreamer(this);
            break;
        }
        case 3: {
            ec = (EdgeComponent *) new EdgeSocket(this);
            break;
        }
        case 4: {
            ec = (EdgeComponent *) new EdgeTracker(this);
            break;
        }
        default:
            edge_logger->logger->error(fmt::format("unknown component name {}", component_name));
            break;
    }
    if (ec) {
        components[component_name] = ec;
    }

    // log
    this->edge_logger->logger->info(fmt::format("register component {} success", component_name));
}

void EdgeApp::initialize() {
    // do real init
    for (auto entry : components) {
        entry.second->init();
        this->edge_logger->logger->info(fmt::format("component {} initialize success", entry.first));
    }
}

void EdgeApp::start_components() {
    // do real start
    for (auto entry: components) {
        entry.second->start();
        // log
        this->edge_logger->logger->info(fmt::format("component {} start success", entry.first));
    }
    for (auto entry: components) {
        entry.second->join();
    }
}

EdgeComponent *EdgeApp::get_components_by_name(std::string component_name) {
    if (components.count(component_name) > 0) {
        return components[component_name];
    }
    return nullptr;
}

void EdgeApp::stop() {
    // do real stop
    for (auto entry: components) {
        entry.second->stop();
    }
    // log
    this->edge_logger->logger->info(fmt::format("component {} stop success", "default"));
}

path EdgeApp::get_file_path(string file_path) {
    return root_path / path(file_path);
}
