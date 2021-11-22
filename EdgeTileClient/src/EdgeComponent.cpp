//
// Created by Xu Wang on 2019/12/15.
//

#include "EdgeComponent.hpp"
#include "EdgeApp.hpp"

using namespace Edge;
EdgeComponent::EdgeComponent(Edge::EdgeApp *app, std::string component_name) {
    this->app = app;
    this->component_name = component_name;
    this->edge_logger = app->edge_logger->getChild(component_name);
    this->config = app->config["components"][component_name];
    this->init_status = false;
}

void EdgeComponent::start() {
    edge_logger->logger->info(fmt::format("{} thread start running", component_name));
    pthread_create(&this->tid, NULL, &EdgeComponent::run_func, this);
}

void EdgeComponent::init() {
    this->initialize();
    this->init_status = true;
    edge_logger->logger->info(fmt::format("{} component init success", component_name));
}

bool EdgeComponent::is_init() {
    return this->init_status;
}

bool EdgeComponent::is_stopped() {
    if(thread_status == PTHREAD_EXIT){
        return true;
    }
    else{
        return false;
    }
}

void * EdgeComponent::run_func(void *context) {
    EdgeComponent* c = (EdgeComponent*) context;
    c->run();
    return NULL;
}

void EdgeComponent::stop() {

}

void EdgeComponent::join() {
    pthread_join(tid, NULL);
}

void EdgeComponent::yield(shared_ptr<EdgePacket> packet) {
    app->handle_yield(this, packet);
}