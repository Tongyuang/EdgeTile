//
// Created by Xu Wang on 2019/12/14.
//

#include "EdgeLog.hpp"
#include "spdlog/sinks/stdout_color_sinks.h"
#include "spdlog/sinks/basic_file_sink.h"
#include "spdlog/fmt/fmt.h"

Edge::EdgeLog::EdgeLog(std::string log_name, std::string document_path) {
    this->log_name = log_name;
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    console_sink->set_level(spdlog::level::trace);
    spdlog::set_pattern("%Y-%m-%d %H:%M:%S,%e - %n - %l - %v");

    auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(
            fmt::format("{}/{}.log", document_path, this->log_name), true);
    file_sink->set_level(spdlog::level::trace);
    //file_sink->set_pattern("%Y-%m-%d %H:%M:%S.%e - %n - %l - %v");
    std::vector<spdlog::sink_ptr> sinks{console_sink, file_sink};
    auto logger = std::make_shared<spdlog::logger>(this->log_name, sinks.begin(), sinks.end());
    spdlog::initialize_logger(logger);
    this->logger = logger;
}
Edge::EdgeLog::EdgeLog(std::string log_name) {
    this->log_name = log_name;
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    console_sink->set_level(spdlog::level::trace);
    spdlog::set_pattern("%Y-%m-%d %H:%M:%S.%e - %n - %l - %v");

    auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(fmt::format("logs/{}.log", this->log_name), true);
    file_sink->set_level(spdlog::level::trace);
    //file_sink->set_pattern("%Y-%m-%d %H:%M:%S.%e - %n - %l - %v");
    std::vector<spdlog::sink_ptr> sinks {console_sink, file_sink};
    auto logger = std::make_shared<spdlog::logger>(this->log_name, sinks.begin(), sinks.end());
    spdlog::initialize_logger(logger);
    this->logger = logger;
}

Edge::EdgeLog::EdgeLog(std::string log_name, std::shared_ptr<spdlog::logger> parent) {
    this->log_name = log_name;
    auto logger = std::make_shared<spdlog::logger>(this->log_name, parent->sinks().begin(), parent->sinks().end());
    spdlog::initialize_logger(logger);
    this->logger = logger;
}


Edge::EdgeLog *Edge::EdgeLog::getChild(std::string child_name) {
    auto log_name = std::string(this->log_name);
    log_name.append(".").append(child_name);
    EdgeLog *logger = new Edge::EdgeLog(log_name, this->logger);
    return logger;
}
