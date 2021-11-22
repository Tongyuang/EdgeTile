//
// Created by Xu Wang on 2019/12/14.
//

#ifndef EDGETILECPP_EDGELOG_HPP
#define EDGETILECPP_EDGELOG_HPP

#include <string>
#include "spdlog/spdlog.h"
namespace Edge {
    class EdgeLog {
    public:
        EdgeLog(std::string log_name, std::string log_path);
        EdgeLog(std::string log_name);
        EdgeLog(std::string, std::shared_ptr<spdlog::logger> parent);
        EdgeLog *getChild(std::string child_name);

    public:
        std::shared_ptr<spdlog::logger> logger;

    private:
        std::string log_name;

    };
}


#endif //EDGETILECPP_EDGELOG_HPP
