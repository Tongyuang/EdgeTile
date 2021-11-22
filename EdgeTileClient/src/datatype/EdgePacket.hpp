//
// Created by Xu Wang on 2020/5/30.
//

#ifndef EDGETILECPP_EDGEPACKET_HPP
#define EDGETILECPP_EDGEPACKET_HPP
#include <string>
using namespace std;
// basic data unit
namespace Edge {
    class EdgeFrame;
    class EdgePacket {
    public:
        EdgePacket(string dt);
        string data_type;
        virtual string toString();

    };
}

#endif //EDGETILECPP_EDGEPACKET_HPP
