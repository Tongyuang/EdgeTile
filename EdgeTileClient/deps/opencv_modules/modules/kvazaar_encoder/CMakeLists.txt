set(the_description "kvazaar encoder module")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} .)
SET(CMAKE_CXX_FLAGS "-O3 -msse3 -g -Wall -Wno-unused-function -std=c++11")
include_directories(${CMAKE_CURRENT_BINARY_DIR})
ocv_include_directories(${CMAKE_SOURCE_DIR}/include)
link_directories(${CMAKE_SOURCE_DIR}/../../../lib)
ocv_define_module(kvazaar_encoder opencv_core kvazaar WRAP)






