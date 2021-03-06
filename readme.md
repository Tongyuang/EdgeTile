#  毕设

EdgeTile 边端协同实时目标检测

随着智能物联网的发展，在算力有限的设备上实现准确、实时的目标检测在交通监控，安全检查等领域具有越来越广泛的运用前景。然而，基于深度学习的目标检测模型为了高精度与实时性，往往需要高算力支持，这让其很难被部署到端系统上。解决上述矛盾的方法主要有两种：1. 减小模型的参数量，使其直接在算力有限的设备上运行，以满足目标检测的实时性要求。这种方法往往导致检测精度很低。2. 利用云端或边缘服务器。例如，将高清视频上传至服务器进行目标检测，将结果再传回本地设备。这种方法在网络波动较强时时往往会导致检测的实时性很差。
  
为了解决上述问题，本系统采用了一种新的边缘服务器-端系统协同检测的方法：在本地设备上对高清视频进行预处理，选择性上传关键帧到边缘服务器进行预测；采用切片-并行传输的方式减小传输时延；并使用目标追踪的方式输出最终的检测结果。本文中，基于嵌入式神经网络处理器的端系统与边缘服务器协同工作，实现了高清视频目标检测任务。实验表明，本文采用的切片-并行的传输方式减小了5.9\%左右的整体传输时延。本系统的边端协同方法能够在端系统上实现帧率为30FPS，分辨率为1080P高清视频的实时目标检测。


端系统：RK3399Pro

边缘系统：高算力服务器

credit to : Xu Wang:https://github.com/aiot-vision/EdgeTileClient.git
