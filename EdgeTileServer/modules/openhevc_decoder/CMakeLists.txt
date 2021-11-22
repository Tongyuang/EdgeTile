set(the_description "openhevc decoder module")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR})
SET(CMAKE_CXX_FLAGS "-O3 -msse3 -g -Wall -Wno-unused-function -std=c++11")

include_directories(${CMAKE_CURRENT_BINARY_DIR})
ocv_include_directories("/usr/local/include")
include_directories(${CMAKE_SOURCE_DIR}/../../dist/openHEVC/include)
link_directories(${CMAKE_SOURCE_DIR}/../../dist/openHEVC/lib)

ocv_define_module(openhevc_decoder opencv_core opencv_imgproc opencv_highgui LibOpenHevcWrapper WRAP python)




