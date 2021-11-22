#include "../../src/utils/Utils.hpp"
#include "../../src/include/EdgeClient.hpp"
#include <iostream>
using namespace std;
using namespace Edge;

void run_app(){
    string config_path = "config/config.yaml";
    string root_path = "/Users/wujiahang/Project/EdgeTile/EdgeTileClient";
    auto config = YAML::LoadFile(config_path);
    auto exp_dir = config["client"]["exp_dir"].Scalar();
    auto client = new EdgeClient(root_path, config);
    client->start();

}

int main(int argc, const char *argv[]) {
    run_app();
}
