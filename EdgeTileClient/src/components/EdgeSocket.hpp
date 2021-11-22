
#ifndef EDGETILECPP_EDGESOCKET_HPP
#define EDGETILECPP_EDGESOCKET_HPP

#include <nlohmann/json.hpp>
#include <sockpp/tcp_connector.h>
#include "../EdgeComponent.hpp"

using namespace nlohmann;
using namespace sockpp;

namespace Edge {
    class EdgeSocket : public EdgeComponent {
    public:
        explicit EdgeSocket(EdgeApp *app);

        void run() override;

        void initialize() override;

        void shutdown();

    private:
        json recv();

        tcp_connector conn;

    };
}


#endif //EDGETILECPP_EDGESOCKET_HPP
