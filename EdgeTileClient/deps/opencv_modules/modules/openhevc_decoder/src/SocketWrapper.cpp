//
//  SocketWrapper.cpp
//  HEVCDecoder
//
//  Created by Xu Wang on 2019/11/19.
//  Copyright © 2019 Xu Wang. All rights reserved.
//

#include "precomp.hpp"
#include <unistd.h>
#include <sys/socket.h>

int read_sock(int sock, void* data, int len)
{
    return (int)read(sock, data, len);
}
