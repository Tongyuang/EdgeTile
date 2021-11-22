#!/bin/bash
PYTHON3_EXECUTABLE=`which python`
PYTHON_INCLUDE_DIRS="$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")" 
PYTHON_LIBRARIES="$(python -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))")"

HEVC_BUILD='build/openHEVC'
HEVC_INSTALL='dist/openHEVC'
KVAZAAR_INSTALL='dist/kvazaar'
OPENCV_BUILD='build/opencv'
OPENCV_INSTALL='dist/opencv'
PACKAGE_INSTALL='dist/python3'

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
check_directory HEVC_BUILD OPENCV_BUILD HEVC_INSTALL KVAZAAR_INSTALL OPENCV_INSTALL PACKAGE_INSTALL LOG_DIR IMG_DIR

install_requirements(){
 cd "$ROOT_DIR" 
 pip install -r requirements.txt
}

build_kvazaar(){
  export CFLAGS="-O3"
  cd "$ROOT_DIR"
  cd "libs/kvazaar"
  sh autogen.sh
  ./configure --prefix=$KVAZAAR_INSTALL
   make -j8
}

install_kvazaar(){
  cd "$ROOT_DIR"
  cd "libs/kvazaar"
  make install
}

build_openHEVC(){
  cd "$ROOT_DIR"
  cd "libs/openHEVC"
  git checkout hevc_rext
  git pull origin hevc_rext
  cd "$HEVC_BUILD"
  cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$HEVC_INSTALL" ../../libs/openHEVC
  make -j8
}

install_openHEVC(){
  cd "$HEVC_BUILD"
  make install
}

build_opencv(){
  cd "$ROOT_DIR"
  export LIBRARY_PATH="$ROOT_DIR/dist/kvazaar/lib:$ROOT_DIR/dist/openHEVC/lib"
  cp dist/kvazaar/include/kvazaar.h modules/kvazaar_encoder/include/opencv2/ 
  cp dist/openHEVC/include/openHevcWrapper.h modules/openhevc_decoder/include/opencv2/
  cd "$OPENCV_BUILD"
  cmake -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$OPENCV_INSTALL" \
  -DWITH_FFMPEG=ON \
  -DBUILD_LIST=core,videoio,opencv_plot,python_bindings_generator,python3,openhevc_decoder,tracking \
  -DOPENCV_EXTRA_MODULES_PATH="../../modules" \
  -DBUILD_opencv_python3=ON \
  -DOPENCV_SKIP_PYTHON_LOADER=ON \
  -DOPENCV_PYTHON3_INSTALL_PATH="$PACKAGE_INSTALL" \
  -DPYTHON3_EXECUTABLE="$PYTHON3_EXECUTABLE" \
  -DPYTHON_INCLUDE_DIRS="$PYTHON_INCLUDE_DIRS" \
  -DPYTHON_LIBRARIES="$PYTHON_LIBRARIES" \
  -DSOFTFP=ON "../../libs/opencv"
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
  echo "[1] install python requirements"
  echo "[2] build kvazaar"
  echo "[3] install kvazaar"
  echo "[4] build openHEVC"
  echo "[5] install openHEVC"
  echo "[6] build opencv"
  echo "[7] install opencv"
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
  1) install_requirements
    ;;
  2) build_kvazaar
    ;;
  3) install_kvazaar
    ;;
  4) build_openHEVC
    ;;
  5) install_openHEVC
    ;;
  6) build_opencv
    ;;
  7) install_opencv
    ;;
  *)
    echo "Thanks, Bye"
    break
    ;;
  esac
  echo ""
done
