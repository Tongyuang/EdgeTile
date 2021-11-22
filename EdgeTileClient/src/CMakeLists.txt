cmake_minimum_required(VERSION 3.2)
project(client)
# for pthread
find_package(Threads REQUIRED)
# Source files
file(GLOB_RECURSE SOURCES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.cpp *.cc)

# Headers
file(GLOB_RECURSE HEADERS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.hpp *.h)


if(PLATFORM STREQUAL "OS64")
    message("compile for ios")
    list(REMOVE_ITEM SOURCES "main.cpp")
    list(REMOVE_ITEM HEADERS "main.h")
    include_directories(
            SYSTEM
            .
            ${CMAKE_SOURCE_DIR}/lib-ios/opencv
            ${CMAKE_SOURCE_DIR}/lib-ios
            ${CMAKE_SOURCE_DIR}/lib-ios/opencv/opencv2.framework
            ${CMAKE_SOURCE_DIR}/../include
    )

    # 从HEADERS列表中找出所有头文件，并放入INCLUDE_FILES变量中
    set(INCLUDE_FILES "")
    foreach (file ${HEADERS})
        # 通过识别".h"子字符串的方式得出一个文件是否是头文件，所以.h和.hpp文件都会被找到
        string(FIND ${file} ".h" pos REVERSE)
        if (NOT ${pos} MATCHES "-1")
            message(STATUS "header file: ${file}")
            list(APPEND INCLUDE_FILES ${file})
        endif ()
    endforeach (file)
    set(INCLUDE_FILES ${INCLUDE_FILES} CACHE INTERNAL "List of include files" FORCE)
    message("INCLUDE_FILES: ${INCLUDE_FILES}")


    #find_library(OPENCV_UNIT NAMES opencv2 HINTS "${CMAKE_SOURCE_DIR}/lib/opencv/opencv2.framework")
    #if (NOT OPENCV_UNIT)
    #    message(FATAL_ERROR "opencv2.framework NOT found!")
    #else()
    #    message(STATUS "opencv2.framework found!")
    #endif()


    add_library(client STATIC
            ${SOURCES}
            ${HEADERS})

    # 这里链接了第三方库：opencv.framework和几个系统库
    set_target_properties(client PROPERTIES
            LINK_FLAGS "-W1,-F${CMAKE_SOURCE_DIR}/lib/opencv/opencv2.framework"
            FRAMEWORK_SEARCH_PATHS "${CMAKE_SOURCE_DIR}/lib/opencv"
            )
    install(TARGETS client DESTINATION ${CMAKE_INSTALL_LIB_DIR})
    target_link_libraries(client
            "-framework UIKit"
            "-framework AssetsLibrary"
            "-framework AVFoundation"
            "-framework CoreFoundation"
            "-framework Foundation"
            "-framework CoreMedia"
            "-framework CoreVideo"
            "-framework CoreGraphics"
            "-framework opencv2"
            yaml-cpp sockpp pugixml
            nlohmann_json::nlohmann_json ${CMAKE_THREAD_LIBS_INIT})



    set_xcode_property(client GCC_GENERATE_DEBUGGING_SYMBOLS YES "ALL")
    set_target_properties(client PROPERTIES
            FRAMEWORK TRUE
            FRAMEWORK_VERSION A
            VERSION 1.0.0
            SOVERSION 1.0.0
            )

    # 将INCLUDE_FILES变量中的所有文件按其路径名放入client.framework/Headers中
    foreach(hfile ${INCLUDE_FILES})
        # 截取出hfile变量中的路径
        string(FIND ${hfile} "/" pos REVERSE)  # 得出最后一个"/"的位置pos
        string(SUBSTRING ${hfile} 0 ${pos} dir)
        message(STATUS "subDir: ${dir}")
        # MACOSX_PACKAGE_LOCATION关键字可以将文件复制到特定的路径中，在IOS framework中，
        # 就是<name>.framework/
        string(FIND ${dir} ".h" isHeader REVERSE)
        if(${isHeader} MATCHES "-1")
            set_property(SOURCE ${hfile} PROPERTY
                    MACOSX_PACKAGE_LOCATION Headers/${dir})
        else()
            set_property(SOURCE ${hfile} PROPERTY
                    MACOSX_PACKAGE_LOCATION Headers)
        endif()
    endforeach(hfile)

else()
    message("compile for desktop")

    link_directories("${CMAKE_INSTALL_LIB_DIR}/opencv/lib")
    # link_directory must write before add_executable
    add_executable(client ../apps/client/main.cpp ${SOURCES} ${HEADERS})
    target_link_libraries(client yaml-cpp sockpp pugixml opencv_kvazaar_encoder opencv_features2d opencv_core opencv_highgui opencv_video opencv_dnn opencv_videoio opencv_imgcodecs opencv_imgproc opencv_tracking nlohmann_json::nlohmann_json ${CMAKE_THREAD_LIBS_INIT})
    install(TARGETS client DESTINATION ${CMAKE_INSTALL_BINDIR})


endif()

