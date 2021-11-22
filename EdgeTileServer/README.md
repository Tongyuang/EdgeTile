# EdgeTile-client


* first compile kvazaar to dynamic lib,  use c module to call kvazaar to encode frames
* the python module is the main module, using opencv to bridge python and c

## Install
* install yasm first
* run compile_module.sh


## the python module

## the C module
- 编译kvazaar模块
- 编译opencv 模块
cmake如果找不到python3的路径需要手动指定一下，最后会编译得到.so 在python中引入该文件的路径就可以使用该模块了，cmake找不到kvazaar.h的头文件，不知道怎么修改，目前是将该头文件拷贝到module的目录下面

```shell
cmake -DCMAKE_BUILD_TYPE=Release \
-DCMAKE_INSTALL_PREFIX=/Users/wangxu/opencv_build \
-DBUILD_LIST=core,videoio,python_bindings_generator,python3,kvazaar_encoder,openhevc_decoder \
-DOPENCV_EXTRA_MODULES_PATH=/Users/wangxu/Git/EdgeTile-Client/modules/ \
-DBUILD_opencv_python3=ON \
-DOPENCV_SKIP_PYTHON_LOADER=ON \
-DOPENCV_PYTHON3_INSTALL_PATH=/Users/wangxu/opencv_build/dist-packages \
-DPYTHON3_EXECUTABLE=/Users/wangxu/miniconda3/envs/py36/bin/python \
-DPYTHON_INCLUDE_DIRS=/Users/wangxu/miniconda3/envs/py36/include \
-DPYTHON_LIBRARIES=/Users/wangxu/miniconda3/envs/py36/lib/libpython3.6m.dylib \
-DSOFTFP=ON ..
```
- 测试效果
`hevc -i test_0.hevc -o test_0 -n`
`ffplay -s 1280x720 file.yuv`

## 生成requirements.txt
`pipreqs --forece ./`


