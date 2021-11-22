#!/usr/bin/env bash
#!/bin/bash
PYTHON3_EXECUTABLE=$(command -v python)
PYTHON_INCLUDE_DIRS="$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")"
PYTHON_LIBRARIES="$(python -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))")"

KVAZAAR_INSTALL='lib/kvazaar'
OPENCV_BUILD='build/opencv'
OPENCV_INSTALL='lib/opencv'
PACKAGE_INSTALL='lib/python3'
LOG_DIR='data/log'
IMG_DIR='data/jpg'

check_directory(){
  ROOT_DIR="$(pwd)"
  echo "work directory is: $ROOT_DIR"
  for var in "$@"
  do
    if eval [ ! -d \$$var ] ; then
      eval echo "create folder \$$var"
      eval mkdir -p \$$var
    fi
    eval $var="$ROOT_DIR/\$$var"
  done
}
check_directory OPENCV_BUILD KVAZAAR_INSTALL OPENCV_INSTALL PACKAGE_INSTALL LOG_DIR IMG_DIR

build_kvazaar(){
  export CFLAGS="-O3"
  cd "$ROOT_DIR"
  cd "deps/kvazaar"
  sh autogen.sh
  ./configure --prefix=$KVAZAAR_INSTALL
   make -j8
}

install_kvazaar(){
  cd "$ROOT_DIR"
  cd "deps/kvazaar"
  make install
}


build_opencv(){
  cd "$ROOT_DIR"
  export LIBRARY_PATH="$ROOT_DIR/lib/kvazaar/lib"
  cp lib/kvazaar/include/kvazaar.h deps/opencv_modules/kvazaar_encoder/include/opencv2/
  cd "$OPENCV_BUILD"
  cmake -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$OPENCV_INSTALL" \
  -DWITH_FFMPEG=ON \
  -DBUILD_LIST=core,highgui,videoio,opencv_plot,python_bindings_generator,python3,kvazaar_encoder,tracking \
  -DOPENCV_EXTRA_MODULES_PATH="../../deps/opencv_modules/modules" \
  -DBUILD_opencv_python3=ON \
  -DOPENCV_SKIP_PYTHON_LOADER=ON \
  -DOPENCV_PYTHON3_INSTALL_PATH="$PACKAGE_INSTALL" \
  -DPYTHON3_EXECUTABLE="$PYTHON3_EXECUTABLE" \
  -DPYTHON_INCLUDE_DIRS="$PYTHON_INCLUDE_DIRS" \
  -DPYTHON_LIBRARIES="$PYTHON_LIBRARIES" \
  -DSOFTFP=ON "../../deps/opencv"
  make -j8
}
  # -DPYTHON_INCLUDE_DIRS="$PYTHON_INCLUDE_DIRS" \
  # -DPYTHON_LIBRARIES="$PYTHON_LIBRARIES" \

install_opencv(){
  cd "$OPENCV_BUILD"
  make install
  echo "Remember to add kvazaar and openHEVC to LD_LIBRARY_PATH"
}

echo "***Compile components for EdgeTile***"
echo ""

while :
do
  echo "[1] build kvazaar"
  echo "[2] install kvazaar"
  echo "[3] build opencv"
  echo "[4] install opencv"
  echo "[0] exit"
  echo "Please ENTRE number to continue"
  printf "[0] >>> "
  read -r -n1 option
  echo ""
  case $option in
  0)
    echo "Thanks, Bye"
    break
    ;;
  1) build_kvazaar
    ;;
  2) install_kvazaar
    ;;
  3) build_opencv
    ;;
  4) install_opencv
    ;;
  *)
    echo "Thanks, Bye"
    break
    ;;
  esac
  echo ""
done

