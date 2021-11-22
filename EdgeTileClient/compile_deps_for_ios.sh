#!/usr/bin/env bash
#!/bin/sh
# 
# compile_deps_for_ios.sh
# EdgeTileIOS
# 
# Created by Jiahang Wu on 2020/3/2.
# Copyright © 2020 Jiahang Wu. All rights reserved.
# 

BASEDIR="$(pwd)"

KVAZAAR_INSTALL='lib-ios/kvazaar'
OPENCV_BUILD='build-ios/opencv'
OPENCV_INSTALL='lib-ios/opencv'
RELEASE_LIB='release_ios'
KVAZAAR_BUILD='deps/kvazaar'
IOS_WORKSPACE='../EdgeTileIOS'
check_directory(){
  echo "work directory is: $BASEDIR"
  for var in "$@"
  do
    if eval [ ! -d \$$var ] ; then
      eval echo "create folder \$$var"
      eval mkdir -p \$$var
    fi
    eval $var="$BASEDIR/\$$var"
  done
}

check_directory KVAZAAR_INSTALL OPENCV_BUILD OPENCV_INSTALL

#build_old_kvazaar_for_ios(){
#  cd ${BASEDIR}/${KVAZAAR_BUILD}-ff
#  make distclean
#
#  cd ${BASEDIR}/${KVAZAAR_BUILD}-ff|| exit 1
#  export CFLAGS="-arch arm64 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS13.2.sdk -miphoneos-version-min=13.0 -fembed-bitcode -DNDEBUG -Wno-sign-compare -O3"
#
#  ./autogen.sh || exit 1
#
#  ./configure \
#      --prefix=${KVAZAAR_INSTALL} \
#      --with-pic \
#      --enable-static \
#      --disable-shared \
#      --disable-fast-install \
#      --host=arm-apple-darwin || exit 1
#
#  make -j8 || exit 1
#  echo "build_old_kvazaar_for_ios() over!"
#}
#
#install_old_kvazaar_for_ios(){
#  cd ${BASEDIR}/${KVAZAAR_BUILD}-ff
#  make install || exit 1
#  echo "INSTALL kvazaar for ios FINISHED!"
#
#  echo "install_old_kvazaar_for_ios() over!"
#
##  exit
#}
build_kvazaar_for_ios(){
  cd ${BASEDIR}/${KVAZAAR_BUILD}
  make distclean

  cd ${BASEDIR}/${KVAZAAR_BUILD}|| exit 1
  export CFLAGS="-arch arm64 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS13.6.sdk -miphoneos-version-min=13.0 -fembed-bitcode -DNDEBUG -Wno-sign-compare -O3"

  ./autogen.sh || exit 1

  ./configure \
      --prefix=${KVAZAAR_INSTALL} \
      --with-pic \
      --enable-static \
      --disable-shared \
      --disable-fast-install \
      --host=arm-apple-darwin || exit 1

  make -j8 || exit 1
  echo "build_kvazaar_for_ios() over!"
  install_kvazaar_for_ios
}

install_kvazaar_for_ios(){
  cd ${BASEDIR}/${KVAZAAR_BUILD}
  make install || exit 1
  echo "INSTALL kvazaar for ios FINISHED!"

  echo "Copy the libkvazaar.a to EdgeTileCamera."
  cd "${BASEDIR}"
  cp lib-ios/kvazaar/lib/libkvazaar.a release_ios/
  echo "install_kvazaar_for_ios() over!"
  build_and_install_opencv_for_ios
#  exit
}

build_and_install_opencv_for_ios(){
#  rm -rf ${BASEDIR}/lib/opencv
#  echo "Delete \"${BASEDIR}/lib/opencv\" directory..."

  cd "${BASEDIR}"
  cp lib-ios/kvazaar/include/kvazaar.h deps/opencv_modules/modules/kvazaar_encoder/include/opencv2/


  /usr/bin/python deps/opencv/platforms/ios/build_framework.py lib-ios/opencv \
  --iphoneos_archs arm64 \
  --contrib "${BASEDIR}/deps/opencv_modules" \
  --build_list "core,video,videoio,opencv_plot,kvazaar_encoder,tracking,highgui,dnn,features2d" \
  --iphoneos_deployment_target 13.0 || exit 1
  echo "BUILD and INSTALL opencv for ios FINISHED!"

  echo "Copy the opencv2.framework and kvazaar headers to /include."
  cd "$BASEDIR"
  rm -rf include/opencv2/*
  cp lib-ios/kvazaar/include/kvazaar.h include/opencv2/
  cp deps/opencv_modules/modules/kvazaar_encoder/include/opencv2/global.h include/opencv2/
  cp -r lib-ios/opencv/opencv2.framework/Headers/* include/opencv2/
  rm -rf ${IOS_WORKSPACE}/include/opencv/*
  cp include/opencv2/* ${IOS_WORKSPACE}/include/opencv
  cp -r lib-ios/opencv/opencv2.framework release_ios/
  echo "build_and_install_opencv_for_ios() over!"
  build_all_for_ios
}

build_all_for_ios(){
#
#  rm -rf ${BASEDIR}/build
#  echo "Delete \"build\" directory..."

  cd "${BASEDIR}"
  cd build-ios

  cmake .. -GXcode \
  -DCMAKE_TOOLCHAIN_FILE="../ios.toolchain.cmake" \
  -DDEPLOYMENT_TARGET=13.0 \
  -DCMAKE_XCODE_ATTRIBUTE_DEVELOPMENT_TEAM="VXYSSFBB5M" \
  -DCMAKE_C_FLAGS=-fembed-bitcode \
  -DCMAKE_CXX_FLAGS=-fembed-bitcode \
  -DPLATFORM=OS64 || exit 1

  cmake --build . --config Release --target install || exit 1
  echo "BUILD and INSTALL all for ios FINISHED!"
  echo "build_all_for_ios() over!"
  cd "${BASEDIR}"
  cp -r lib-ios/client.framework release_ios/
  cp lib-ios/libpugixml.a release_ios/
  cp lib-ios/libspdlog.a  release_ios/
  cp lib-ios/libsockpp.a  release_ios/
  cp lib-ios/kvazaar/lib/libkvazaar.a  release_ios/
  cp lib-ios/libyaml-cpp.a release_ios/

  rm -rf ${IOS_WORKSPARCE}/include/client/*
  cp -r release_ios/client.framework/Headers/* ${IOS_WORKSPACE}/include/client/
  cp -r release_ios/*.framework ${IOS_WORKSPACE}
  cp release_ios/*.a ${IOS_WORKSPACE}
  exit
}

echo "*** Compile components for EdgeTileForIOS ***"
echo ""

while :
do
  echo "[1] build kvazaar for IOS"
  echo "[2] install kvazaar for IOS"
  echo "[3] build and install opencv for IOS"
  echo "[4] build all for IOS"
  echo "[0] exit"
  echo "Please ENTRE number to continue"
  printf "[0] >>> "
  read -r option
  echo ""
  case $option in
  0)
    echo "Thanks, Bye"
    break
    ;;
  1) build_kvazaar_for_ios
    ;;
  2) install_kvazaar_for_ios
    ;;
  3) build_and_install_opencv_for_ios
    ;;
  4) build_all_for_ios
    ;;
  *)
    echo "Thanks, Bye"
    break
    ;;
  esac
  echo ""
done
