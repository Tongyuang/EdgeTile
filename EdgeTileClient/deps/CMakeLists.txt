cmake_minimum_required(VERSION 3.2)
project(deps)


add_subdirectory(yaml-cpp)
add_subdirectory(spdlog)
add_subdirectory(sockpp)
add_subdirectory(json)
add_subdirectory(pugixml)

install(FILES ${PROJECT_SOURCE_DIR}/concurrentqueue/concurrentqueue.h
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/concurrentqueue/)
install(FILES ${PROJECT_SOURCE_DIR}/concurrentqueue/blockingconcurrentqueue.h
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/concurrentqueue/)




