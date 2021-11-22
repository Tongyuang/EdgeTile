# CMakeLists.txt
#
# Top-level CMake build file for the 'sockpp' library.
#
# ---------------------------------------------------------------------------
# This file is part of the "sockpp" C++ socket library.
#
# Copyright (c) 2017-2018 Frank Pagliughi
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ---------------------------------------------------------------------------

## CMake required version
cmake_minimum_required(VERSION 3.5)

## project
project(sockpp VERSION "0.7.0")

## library name
set(SOCKPP sockpp)
set(SOCKPP_STATIC ${SOCKPP}-static)

# --- Build Options ---

if (WIN32)
    option(SOCKPP_BUILD_STATIC "Build static library" ON)
    option(SOCKPP_BUILD_SHARED "Build shared library (DLL)" OFF)
else ()
    option(SOCKPP_BUILD_STATIC "Build static library" ON)
    option(SOCKPP_BUILD_SHARED "Build shared library" OFF)
endif ()

option(SOCKPP_BUILD_EXAMPLES "Build example applications" OFF)
option(SOCKPP_BUILD_TESTS "Build unit tests" OFF)
option(SOCKPP_BUILD_DOCUMENTATION "Create Doxygen refe\\\\\rence documentation" OFF)

# --- C++14 build flags ---

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)

# --- Generate a version header ---

#configure_file(
#        ${CMAKE_CURRENT_SOURCE_DIR}/version.h.in
#        generated/${SOCKPP}/version.h
#        @ONLY
#)
include_directories(${sockpp_SOURCE_DIR}/include)
message("sockpp ${sockpp_SOURCE_DIR}/include")
# --- Common Library Sources, etc ---

#add_subdirectory(src)
set(SOURCES
        src/acceptor.cpp
        src/connector.cpp
        src/datagram_socket.cpp
        src/exception.cpp
        src/inet_address.cpp
        src/inet6_address.cpp
        src/socket.cpp
        src/stream_socket.cpp
        src/unix/unix_address.cpp
        )
# --- Header Locations ---

#target_include_directories(sockpp-objs
#        PUBLIC
#        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
#        $<INSTALL_INTERFACE:include>
#        src
#        )
set(HEADERS
        include/sockpp/acceptor.h
        include/sockpp/connector.h
        include/sockpp/datagram_socket.h
        include/sockpp/exception.h
        include/sockpp/inet_address.h
        include/sockpp/inet6_address.h
        include/sockpp/platform.h
        include/sockpp/sock_address.h
        include/sockpp/socket.h
        include/sockpp/stream_socket.h
        include/sockpp/tcp6_acceptor.h
        include/sockpp/tcp6_connector.h
        include/sockpp/tcp6_socket.h
        include/sockpp/tcp_acceptor.h
        include/sockpp/tcp_connector.h
        include/sockpp/tcp_socket.h
        include/sockpp/udp6_socket.h
        include/sockpp/udp_socket.h
        include/sockpp/unix_acceptor.h
        include/sockpp/unix_address.h
        include/sockpp/unix_connector.h
        include/sockpp/unix_dgram_socket.h
        include/sockpp/unix_stream_socket.h
        )


# --- System libraries ---

include(GNUInstallDirs)

if (WIN32)
    set(LIBS_SYSTEM ws2_32)
elseif (UNIX)
    set(LIBS_SYSTEM c stdc++)
endif ()


## --- create the shared library ---

if (SOCKPP_BUILD_SHARED)
    message(STATUS "Creating shared library: ${SOCKPP}")

    add_library(${SOCKPP} SHARED ${SOURCES} ${HEADERS})

    ## add dependencies to the shared library
    target_link_libraries(${SOCKPP} ${LIBS_SYSTEM})



#    set_target_properties(${SOCKPP} PROPERTIES
#            VERSION ${PROJECT_VERSION}
#            SOVERSION ${PROJECT_VERSION_MAJOR})

    install(TARGETS ${SOCKPP}
            DESTINATION ${CMAKE_INSTALL_LIBDIR}
            )

endif ()

# --- Create the static library ---

if (SOCKPP_BUILD_STATIC)
    message(STATUS "Creating static library: ${SOCKPP_STATIC}")

    add_library(${SOCKPP} STATIC ${SOURCES} ${HEADERS})

    ## add dependencies to the shared library
    target_link_libraries(${SOCKPP} ${LIBS_SYSTEM})



    #    set_target_properties(${SOCKPP} PROPERTIES
    #            VERSION ${PROJECT_VERSION}
    #            SOVERSION ${PROJECT_VERSION_MAJOR})

    install(TARGETS ${SOCKPP}
            DESTINATION ${CMAKE_INSTALL_LIBDIR}
            )

    # Let the archive use the same name as the shared library
#    if (UNIX)
#        set_target_properties(${SOCKPP_STATIC} PROPERTIES OUTPUT_NAME ${SOCKPP})
#    endif ()
endif ()

# --- Install the library ---
#
install(DIRECTORY include/${SOCKPP}/
        DESTINATION include/${SOCKPP}
        FILES_MATCHING PATTERN "*.h*")

install(DIRECTORY ${CMAKE_BINARY_DIR}/generated/${SOCKPP}/
        DESTINATION include/${SOCKPP}
        FILES_MATCHING PATTERN "*.h*")

# --- Documentation ---

#if(SOCKPP_BUILD_DOCUMENTATION)
#	add_subdirectory(doc)
#endif()

# --- Default library for examples and unit tests ---

if (SOCKPP_BUILD_SHARED)
    set(SOCKPP_LIB ${SOCKPP})
else ()
    set(SOCKPP_LIB ${SOCKPP_STATIC})
endif ()


# --- Examples Applications ---

if (SOCKPP_BUILD_EXAMPLES)
    add_subdirectory(examples/tcp)
    add_subdirectory(examples/udp)
    if (UNIX)
        add_subdirectory(examples/unix)
    endif ()
endif ()

# --- Unit Tests ---

if (SOCKPP_BUILD_TESTS)
    add_subdirectory(tests/unit)
endif ()

