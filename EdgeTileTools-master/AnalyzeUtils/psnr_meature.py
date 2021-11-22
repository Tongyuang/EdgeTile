from matplotlib import pyplot as plt
import numpy as np
# 该文件用于分析ios上jpeg,hevc的psnr
if __name__ == "__main__":
    gop_size=10
    hevc_encode_862_0_list = []
    hevc_encode_862_10_list = []
    hevc_encode_862_20_list = []
    hevc_encode_862_30_list = []
    hevc_encode_862_40_list = []
    hevc_encode_862_50_list = []

    i_hevc_encode_862_0_list = []
    i_hevc_encode_862_10_list = []
    i_hevc_encode_862_20_list = []
    i_hevc_encode_862_30_list = []
    i_hevc_encode_862_40_list = []
    i_hevc_encode_862_50_list = []

    jpeg_encode_862_0_list = []
    jpeg_encode_862_20_list = []
    jpeg_encode_862_40_list = []
    jpeg_encode_862_60_list = []
    jpeg_encode_862_80_list = []
    jpeg_encode_862_100_list = []

    names = locals()
    for qp in [0,10,20,30,40,50]:
        for resolution in [862]:
            with open('psnr_logs/hevc/encoder_time_{}_{}.log'.format(resolution,qp), 'r', encoding='utf-8') as f:
                for line in f:
                    frame, encode_time, psnr, ssim= int(line.split(
                        ',')[0]), int(line.split(',')[1]),float(line.split(',')[2]),float(line.split(',')[3])
                    names['hevc_encode_{}_{}_list'.format(resolution, qp)].append((frame, encode_time, psnr, ssim))
                    if frame%gop_size == 0:
                        names['i_hevc_encode_{}_{}_list'.format(resolution, qp)].append((frame, encode_time, psnr, ssim))
    
    



    for quality in [0,20,40,60,80,100]:
        for resolution in [862]:
            with open('psnr_logs/jpeg/jpeg_encode_{}_{}.log'.format(quality, resolution), 'r', encoding='utf-8') as f:
                for line in f:
                    frame, encode_time, img_size, psnr, ssim = int(line.split(
                        ',')[0]), int(line.split(',')[1]),int(int(line.split(',')[2])/1000), float(line.split(',')[3]), float(line.split(',')[4])
                    names['jpeg_encode_{}_{}_list'.format(resolution,quality)].append((frame, encode_time,img_size,psnr,ssim))

    plt.close('all') # 清空，重新画
    fig = plt.figure(figsize=(7,5))
    ax = plt.subplot(111)
    
    x = [0, 10, 20, 30, 40, 50]
    y = [
            np.mean([x[2] for x in hevc_encode_862_0_list]),
            np.mean([x[2] for x in hevc_encode_862_10_list]),
            np.mean([x[2] for x in hevc_encode_862_20_list]),
            np.mean([x[2] for x in hevc_encode_862_30_list]),
            np.mean([x[2] for x in hevc_encode_862_40_list]),
            np.mean([x[2] for x in hevc_encode_862_50_list])
        ]
    ax.plot(y, x, linestyle='-', color='green', marker= 'o', label = "HEVC")

    x = [0, 20, 40, 60, 80, 100]
    y = [
            np.mean([x[3] for x in jpeg_encode_862_0_list]),
            np.mean([x[3] for x in jpeg_encode_862_20_list]),
            np.mean([x[3] for x in jpeg_encode_862_40_list]),
            np.mean([x[3] for x in jpeg_encode_862_60_list]),
            np.mean([x[3] for x in jpeg_encode_862_80_list]),
            np.mean([x[3] for x in jpeg_encode_862_100_list])
        ]
    
    ax2 = ax.twinx()
    ax2.plot(y, x, linestyle='-', color='blue', marker= 'o', label = 'JPEG' )
    
    ax.grid()
    ax.set_xlabel("Average PSNR")
    ax.set_ylabel("qp(HEVC encode)", color='green')
    ax2.set_ylabel("quality(JPEG encode)", color='blue')
    plt.title('Relationship between qp&quality and PSNR.(720p)') 
    fig.legend(loc='best', bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
    plt.savefig("analyze_result/720p-qp-quality-psnr.png", bbox_inches='tight', dpi=300)



    plt.close('all') # 清空，重新画 
    fig = plt.figure(figsize=(7,5))
    ax = plt.subplot(111)
    x = [0, 10, 20, 30, 40, 50]
    y = [
            np.mean([x[1] for x in hevc_encode_862_0_list]),
            np.mean([x[1] for x in hevc_encode_862_10_list]),
            np.mean([x[1] for x in hevc_encode_862_20_list]),
            np.mean([x[1] for x in hevc_encode_862_30_list]),
            np.mean([x[1] for x in hevc_encode_862_40_list]),
            np.mean([x[1] for x in hevc_encode_862_50_list])
        ]
    ax.plot(y, x, linestyle='-', color='green', marker= 'o', label='HEVC')

    x = [0, 10, 20, 30, 40, 50]
    y = [
            np.mean([x[1] for x in i_hevc_encode_862_0_list]),
            np.mean([x[1] for x in i_hevc_encode_862_10_list]),
            np.mean([x[1] for x in i_hevc_encode_862_20_list]),
            np.mean([x[1] for x in i_hevc_encode_862_30_list]),
            np.mean([x[1] for x in i_hevc_encode_862_40_list]),
            np.mean([x[1] for x in i_hevc_encode_862_50_list])
        ]
    ax.plot(y, x, linestyle='-', color='red', marker= 'o', label='HEVC I-Frame')

    x = [0, 20, 40, 60, 80, 100]
    x = [0, 20, 40, 60, 80, 100]
    y = [
            np.mean([x[1] for x in jpeg_encode_862_0_list]),
            np.mean([x[1] for x in jpeg_encode_862_20_list]),
            np.mean([x[1] for x in jpeg_encode_862_40_list]),
            np.mean([x[1] for x in jpeg_encode_862_60_list]),
            np.mean([x[1] for x in jpeg_encode_862_80_list]),
            np.mean([x[1] for x in jpeg_encode_862_100_list])
        ]

    ax2 = ax.twinx()
    ax2.plot(y, x, linestyle='-', color='blue', marker= 'o', label="JPEG")
   
    
    ax.grid()
    ax.set_xlabel("Average encode time cost(ms)")
    ax.set_ylabel("qp(HEVC encode)",color='green')
    ax2.set_ylabel("quality(JPEG encode)",color='blue')
    plt.title('Relationship between qp&quality and time cost.(720p)') 

    fig.legend(loc='best', bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
    plt.savefig("analyze_result/720p-qp-quality-time.png", bbox_inches='tight', dpi=300)

    plt.close('all') # 清空，重新画 
    fig = plt.figure(figsize=(7,5))
    ax = plt.subplot(111)
    x = [
            np.mean([x[2] for x in hevc_encode_862_0_list]),
            np.mean([x[2] for x in hevc_encode_862_10_list]),
            np.mean([x[2] for x in hevc_encode_862_20_list]),
            np.mean([x[2] for x in hevc_encode_862_30_list]),
            np.mean([x[2] for x in hevc_encode_862_40_list]),
            np.mean([x[2] for x in hevc_encode_862_50_list])
        ]
    y = [
            np.mean([x[1] for x in hevc_encode_862_0_list]),
            np.mean([x[1] for x in hevc_encode_862_10_list]),
            np.mean([x[1] for x in hevc_encode_862_20_list]),
            np.mean([x[1] for x in hevc_encode_862_30_list]),
            np.mean([x[1] for x in hevc_encode_862_40_list]),
            np.mean([x[1] for x in hevc_encode_862_50_list])
        ]
    ax.plot(x, y, linestyle='-', color='green', marker= 'o', label = "HEVC")

    x = [
            np.mean([x[3] for x in jpeg_encode_862_0_list]),
            np.mean([x[3] for x in jpeg_encode_862_20_list]),
            np.mean([x[3] for x in jpeg_encode_862_40_list]),
            np.mean([x[3] for x in jpeg_encode_862_60_list]),
            np.mean([x[3] for x in jpeg_encode_862_80_list]),
            np.mean([x[3] for x in jpeg_encode_862_100_list])
        ]
    y = [
            np.mean([x[1] for x in jpeg_encode_862_0_list]),
            np.mean([x[1] for x in jpeg_encode_862_20_list]),
            np.mean([x[1] for x in jpeg_encode_862_40_list]),
            np.mean([x[1] for x in jpeg_encode_862_60_list]),
            np.mean([x[1] for x in jpeg_encode_862_80_list]),
            np.mean([x[1] for x in jpeg_encode_862_100_list])
        ]
    
    ax.plot(x, y, linestyle='-', color='blue', marker= 'o',label = "JPEG")
    ax.legend()
    
    ax.grid()
    ax.set_xlabel("Average PSNR")
    ax.set_ylabel("Average encode time cost(ms)")
    plt.title('Relationship between PSNR and time cost.(720p)') 
    plt.savefig("analyze_result/720p-psnr-time.png", bbox_inches='tight', dpi=300)
    
    
    hevc_encode_2464_0_list = []
    hevc_encode_2464_10_list = []
    hevc_encode_2464_20_list = []
    hevc_encode_2464_30_list = []
    hevc_encode_2464_40_list = []
    hevc_encode_2464_50_list = []

    i_hevc_encode_2464_0_list = []
    i_hevc_encode_2464_10_list = []
    i_hevc_encode_2464_20_list = []
    i_hevc_encode_2464_30_list = []
    i_hevc_encode_2464_40_list = []
    i_hevc_encode_2464_50_list = []


    jpeg_encode_2464_0_list = []
    jpeg_encode_2464_20_list = []
    jpeg_encode_2464_40_list = []
    jpeg_encode_2464_60_list = []
    jpeg_encode_2464_80_list = []
    jpeg_encode_2464_100_list = []

    names = locals()
    for qp in [0,10,20,30,40,50]:
        for resolution in [2464]:
            with open('psnr_logs/hevc/encoder_time_{}_{}.log'.format(resolution,qp), 'r', encoding='utf-8') as f:
                for line in f:
                    frame, encode_time, psnr, ssim = int(line.split(
                        ',')[0]), int(line.split(',')[1]),float(line.split(',')[2]),float(line.split(',')[3])
                    names['hevc_encode_{}_{}_list'.format(resolution, qp)].append((frame, encode_time, psnr, ssim))
                    if frame%gop_size == 0:
                        names['i_hevc_encode_{}_{}_list'.format(resolution, qp)].append((frame, encode_time, psnr))



    for quality in [0,20,40,60,80,100]:
        for resolution in [2464]:
            with open('psnr_logs/jpeg/jpeg_encode_{}_{}.log'.format(quality, resolution), 'r', encoding='utf-8') as f:
                for line in f:
                    frame, encode_time, img_size, psnr , ssim= int(line.split(
                        ',')[0]), int(line.split(',')[1]),int(int(line.split(',')[2])/1000), float(line.split(',')[3]),float(line.split(',')[4])
                    names['jpeg_encode_{}_{}_list'.format(resolution,quality)].append((frame, encode_time,img_size,psnr,ssim))

    
    plt.close('all') # 清空，重新画
    fig = plt.figure(figsize=(7,5))
    ax = plt.subplot(111)
    x = [0, 10, 20, 30, 40, 50]
    y = [
            np.mean([x[2] for x in hevc_encode_2464_0_list]),
            np.mean([x[2] for x in hevc_encode_2464_10_list]),
            np.mean([x[2] for x in hevc_encode_2464_20_list]),
            np.mean([x[2] for x in hevc_encode_2464_30_list]),
            np.mean([x[2] for x in hevc_encode_2464_40_list]),
            np.mean([x[2] for x in hevc_encode_2464_50_list])
        ]
    ax.plot(y, x, linestyle='-', color='green', marker= 'o', label = "HEVC")
    
    x = [0, 20, 40, 60, 80, 100]
    y = [
            np.mean([x[3] for x in jpeg_encode_2464_0_list]),
            np.mean([x[3] for x in jpeg_encode_2464_20_list]),
            np.mean([x[3] for x in jpeg_encode_2464_40_list]),
            np.mean([x[3] for x in jpeg_encode_2464_60_list]),
            np.mean([x[3] for x in jpeg_encode_2464_80_list]),
            np.mean([x[3] for x in jpeg_encode_2464_100_list])
        ]
    

    ax2 = ax.twinx()
    ax2.plot(y, x, linestyle='-', color='blue', marker= 'o', label = "JPEG")
    
    
    ax.grid()
    ax.set_xlabel("Average PSNR")
    ax.set_ylabel("qp(HEVC encode)", color='green')
    ax2.set_ylabel("quality(JPEG encode)", color='blue')
    plt.title('Relationship between qp&quality and PSNR.(2k)') 
    fig.legend(loc='best', bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
    plt.savefig("analyze_result/2k-qp-quality-psnr.png", bbox_inches='tight', dpi=300)

    plt.close('all') # 清空，重新画 
    fig = plt.figure(figsize=(7,5))
    ax = plt.subplot(111)
    x = [0, 10, 20, 30, 40, 50]
    y = [
            np.mean([x[1] for x in hevc_encode_2464_0_list]),
            np.mean([x[1] for x in hevc_encode_2464_10_list]),
            np.mean([x[1] for x in hevc_encode_2464_20_list]),
            np.mean([x[1] for x in hevc_encode_2464_30_list]),
            np.mean([x[1] for x in hevc_encode_2464_40_list]),
            np.mean([x[1] for x in hevc_encode_2464_50_list])
        ]
    ax.plot(y, x, linestyle='-', color='green', marker= 'o', label = 'HEVC')
    x = [0, 10, 20, 30, 40, 50]
    y = [
            np.mean([x[1] for x in i_hevc_encode_2464_0_list]),
            np.mean([x[1] for x in i_hevc_encode_2464_10_list]),
            np.mean([x[1] for x in i_hevc_encode_2464_20_list]),
            np.mean([x[1] for x in i_hevc_encode_2464_30_list]),
            np.mean([x[1] for x in i_hevc_encode_2464_40_list]),
            np.mean([x[1] for x in i_hevc_encode_2464_50_list])
        ]
    ax.plot(y, x, linestyle='-', color='red', marker= 'o', label = 'HEVC I-Frames')
    x = [0, 20, 40, 60, 80, 100]
    y = [
            np.mean([x[1] for x in jpeg_encode_2464_0_list]),
            np.mean([x[1] for x in jpeg_encode_2464_20_list]),
            np.mean([x[1] for x in jpeg_encode_2464_40_list]),
            np.mean([x[1] for x in jpeg_encode_2464_60_list]),
            np.mean([x[1] for x in jpeg_encode_2464_80_list]),
            np.mean([x[1] for x in jpeg_encode_2464_100_list])
        ]
    ax2 = ax.twinx()
    ax2.plot(y, x, linestyle='-', color='blue', marker= 'o',label = 'JPEG')
   
    
    ax.grid()
    ax.set_xlabel("Average encode time cost(ms)")
    ax.set_ylabel("qp(HEVC encode)",color='green')
    ax2.set_ylabel("quality(JPEG encode)",color='blue')
    plt.title('Relationship between qp&quality and time cost.(2k)') 
    fig.legend(loc='best', bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
    plt.savefig("analyze_result/2k-qp-quality-time.png", bbox_inches='tight', dpi=300)

    plt.close('all') # 清空，重新画 
    fig = plt.figure(figsize=(7,5))
    ax = plt.subplot(111)
    
    x = [
            np.mean([x[2] for x in hevc_encode_2464_0_list]),
            np.mean([x[2] for x in hevc_encode_2464_10_list]),
            np.mean([x[2] for x in hevc_encode_2464_20_list]),
            np.mean([x[2] for x in hevc_encode_2464_30_list]),
            np.mean([x[2] for x in hevc_encode_2464_40_list]),
            np.mean([x[2] for x in hevc_encode_2464_50_list])
        ]
    y = [
            np.mean([x[1] for x in hevc_encode_2464_0_list]),
            np.mean([x[1] for x in hevc_encode_2464_10_list]),
            np.mean([x[1] for x in hevc_encode_2464_20_list]),
            np.mean([x[1] for x in hevc_encode_2464_30_list]),
            np.mean([x[1] for x in hevc_encode_2464_40_list]),
            np.mean([x[1] for x in hevc_encode_2464_50_list])
        ]
    ax.plot(x, y, linestyle='-', color='green', marker= 'o', label = "HEVC")

    x = [
            np.mean([x[3] for x in jpeg_encode_2464_0_list]),
            np.mean([x[3] for x in jpeg_encode_2464_20_list]),
            np.mean([x[3] for x in jpeg_encode_2464_40_list]),
            np.mean([x[3] for x in jpeg_encode_2464_60_list]),
            np.mean([x[3] for x in jpeg_encode_2464_80_list]),
            np.mean([x[3] for x in jpeg_encode_2464_100_list])
        ]
    y = [
            np.mean([x[1] for x in jpeg_encode_2464_0_list]),
            np.mean([x[1] for x in jpeg_encode_2464_20_list]),
            np.mean([x[1] for x in jpeg_encode_2464_40_list]),
            np.mean([x[1] for x in jpeg_encode_2464_60_list]),
            np.mean([x[1] for x in jpeg_encode_2464_80_list]),
            np.mean([x[1] for x in jpeg_encode_2464_100_list])
        ]
    
    ax.plot(x, y, linestyle='-', color='blue', marker= 'o',label = "JPEG")
    ax.legend()
    
    ax.grid()
    ax.set_xlabel("Average PSNR")
    ax.set_ylabel("Average encode time cost(ms)")
    plt.title('Relationship between PSNR and time cost.(2k)') 
    plt.savefig("analyze_result/2k-psnr-time.png", bbox_inches='tight', dpi=300)
    
    
    