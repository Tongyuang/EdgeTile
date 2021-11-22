from matplotlib import pyplot as plt
import numpy as np
# 该文件用于分析ios上jpeg的编码效率(1280*720,3840*2160)
if __name__ == "__main__":
    gop_size = 10
    hevc_encode_862_10_list = {}
    hevc_encode_862_20_list = {}
    hevc_encode_862_30_list = {}

    hevc_encode_2464_10_list = {}
    hevc_encode_2464_20_list = {}
    hevc_encode_2464_30_list = {}

    i_hevc_encode_862_10_list = {}
    i_hevc_encode_862_20_list = {}
    i_hevc_encode_862_30_list = {}

    i_hevc_encode_2464_10_list = {}
    i_hevc_encode_2464_20_list = {}
    i_hevc_encode_2464_30_list = {}

    jpeg_encode_20_862_list = []
    jpeg_encode_40_862_list = []
    jpeg_encode_60_862_list = []
    jpeg_encode_80_862_list = []
    jpeg_encode_90_862_list = []
    jpeg_encode_100_862_list = []

    jpeg_encode_20_2464_list = []
    jpeg_encode_40_2464_list = []
    jpeg_encode_60_2464_list = []
    jpeg_encode_80_2464_list = []
    jpeg_encode_90_2464_list = []

    names = locals()

    for quality in [20,40,60,80,90]:
        for resolution in [862, 2464]:
            with open('jpeg_encode_logs/jpeg_encode_{}_{}.log'.format(quality, resolution), 'r', encoding='utf-8') as f:
                for line in f:
                    frame, encode_time, img_size = int(line.split(
                        ',')[0]), int(line.split(',')[1]),int(line.split(',')[2])/1000
                    names['jpeg_encode_{}_{}_list'.format(quality, resolution)].append((frame, encode_time,img_size))


    for quality in [10,20,30]:
        for resolution in [862, 2464]:
            with open('hevc_size_logs/encoder_size_{}_{}.log'.format(resolution,quality), 'r', encoding='utf-8') as f:
                for line in f:
                    frame, tile, tile_size = int(line.split(
                        ',')[0]), int(line.split(',')[1]), int(line.split(',')[2])/1000
                    if tile!= -1:
                        if frame in names['hevc_encode_{}_{}_list'.format(resolution,quality)].keys():
                            names['hevc_encode_{}_{}_list'.format(resolution,quality)][frame] += tile_size
                        else:
                            names['hevc_encode_{}_{}_list'.format(resolution,quality)][frame] = tile_size
    # 获取I帧
    for quality in [10,20,30]:
        for resolution in [862, 2464]:
            for key in names['hevc_encode_{}_{}_list'.format(resolution,quality)]:
                if (key)%gop_size == 0:
                    names['i_hevc_encode_{}_{}_list'.format(resolution,quality)][key] = names['hevc_encode_{}_{}_list'.format(resolution,quality)][key]
    
    
    plt.figure(figsize=(14, 7))
    plt.subplot(1,2,1)
    x = ["≈34\n","≈38\n","≈44\n"]
    y1 = [hevc_encode_862_30_list[r] for r in hevc_encode_862_30_list]
    y2 = [hevc_encode_862_20_list[r] for r in hevc_encode_862_20_list]
    y3 = [hevc_encode_862_10_list[r] for r in hevc_encode_862_10_list]
    y_720p = [np.mean(y1),np.mean(y2),np.mean(y3)]
    y1 = [hevc_encode_2464_30_list[r] for r in hevc_encode_2464_30_list]
    y2 = [hevc_encode_2464_20_list[r] for r in hevc_encode_2464_20_list]
    y3 = [hevc_encode_2464_10_list[r] for r in hevc_encode_2464_10_list]
    y_2k = [np.mean(y1),np.mean(y2),np.mean(y3)]
    y1 = [i_hevc_encode_862_30_list[r] for r in i_hevc_encode_862_30_list]
    y2 = [i_hevc_encode_862_20_list[r] for r in i_hevc_encode_862_20_list]
    y3 = [i_hevc_encode_862_10_list[r] for r in i_hevc_encode_862_10_list]
    y_720p_i = [np.mean(y1),np.mean(y2),np.mean(y3)]
    y1 = [i_hevc_encode_2464_30_list[r] for r in i_hevc_encode_2464_30_list]
    y2 = [i_hevc_encode_2464_20_list[r] for r in i_hevc_encode_2464_20_list]
    y3 = [i_hevc_encode_2464_10_list[r] for r in i_hevc_encode_2464_10_list]
    y_2k_i = [np.mean(y1),np.mean(y2),np.mean(y3)]
    x_len= range(len(x))
    plt.bar(x_len, y_720p, color = 'blue', width=0.2, label='862x720')
    plt.bar([i + 0.2 for i in x_len], y_720p_i, color = 'pink', width=0.2, label='862x720 I')
    plt.bar([i + 0.2*2 for i in x_len], y_2k, color = 'green', width=0.2, label='2464x2056')
    plt.bar([i + 0.2*3 for i in x_len], y_2k_i, color = 'orange', width=0.2, label='2464x2056 I')

    plt.title('HEVC Compression') 
    plt.ylabel('Average Frame Size (KB)') 
    plt.xlabel('PSNR') 
    plt.grid(axis="y",color='r',linestyle='--')
    plt.xticks([i + 0.1*2 for i in x_len], x)
    plt.ylim((0, 700))
    plt.legend()

    plt.subplot(1,  2,  2)
    x = ["≈34\n","≈38\n","≈44\n"]
    y1 = [r[2] for r in jpeg_encode_20_862_list]
    y2 = [r[2] for r in jpeg_encode_60_862_list]
    y3 = [r[2] for r in jpeg_encode_90_862_list]
    y_720p = [np.mean(y1),np.mean(y2),np.mean(y3)]
    y1 = [r[2] for r in jpeg_encode_20_2464_list]
    y2 = [r[2] for r in jpeg_encode_60_2464_list]
    y3 = [r[2] for r in jpeg_encode_90_2464_list]
    y_2k = [np.mean(y1),np.mean(y2),np.mean(y3)]
    x_len= range(len(x))
    plt.bar(x_len, y_720p, color = 'blue', width=0.2, label='862x720')
    plt.bar([i + 0.2 for i in x_len], y_2k, color = 'green', width=0.2, label='2464x2056')
    plt.title('JPEG Compression') 
    plt.ylabel('Average Frame Size (KB)') 
    plt.xlabel('PSNR') 
    plt.grid(axis="y",color='r',linestyle='--')
    plt.xticks([i + 0.1 for i in x_len], x)
    plt.ylim((0, 700))
    plt.legend()
    plt.savefig("analyze_result/psnr_size_jpeg_hevc.png", bbox_inches='tight', dpi=300)

    plt.close('all') # 清空，重新画 
    plt.figure(figsize=(14, 7))
    plt.subplot(1,2,1)
    x = ["30\n","20\n","10\n"]
    y1 = [hevc_encode_862_30_list[r] for r in hevc_encode_862_30_list]
    y2 = [hevc_encode_862_20_list[r] for r in hevc_encode_862_20_list]
    y3 = [hevc_encode_862_10_list[r] for r in hevc_encode_862_10_list]
    y_720p = [np.mean(y1),np.mean(y2),np.mean(y3)]
    y1 = [hevc_encode_2464_30_list[r] for r in hevc_encode_2464_30_list]
    y2 = [hevc_encode_2464_20_list[r] for r in hevc_encode_2464_20_list]
    y3 = [hevc_encode_2464_10_list[r] for r in hevc_encode_2464_10_list]
    y_2k = [np.mean(y1),np.mean(y2),np.mean(y3)]
    y1 = [i_hevc_encode_862_30_list[r] for r in i_hevc_encode_862_30_list]
    y2 = [i_hevc_encode_862_20_list[r] for r in i_hevc_encode_862_20_list]
    y3 = [i_hevc_encode_862_10_list[r] for r in i_hevc_encode_862_10_list]
    y_720p_i = [np.mean(y1),np.mean(y2),np.mean(y3)]
    y1 = [i_hevc_encode_2464_30_list[r] for r in i_hevc_encode_2464_30_list]
    y2 = [i_hevc_encode_2464_20_list[r] for r in i_hevc_encode_2464_20_list]
    y3 = [i_hevc_encode_2464_10_list[r] for r in i_hevc_encode_2464_10_list]
    y_2k_i = [np.mean(y1),np.mean(y2),np.mean(y3)]
    x_len= range(len(x))
    plt.bar(x_len, y_720p, color = 'blue', width=0.2, label='862x720')
    plt.bar([i + 0.2 for i in x_len], y_720p_i, color = 'pink', width=0.2, label='862x720 I')
    plt.bar([i + 0.2*2 for i in x_len], y_2k, color = 'green', width=0.2, label='2464x2056')
    plt.bar([i + 0.2*3 for i in x_len], y_2k_i, color = 'orange', width=0.2, label='2464x2056 I')

    plt.title('HEVC Compression') 
    plt.ylabel('Average Frame Size (KB)') 
    plt.xlabel('QP') 
    plt.grid(axis="y",color='r',linestyle='--')
    plt.xticks([i + 0.1*2 for i in x_len], x)
    plt.ylim((0, 700))
    plt.legend()


    plt.subplot(1,  2,  2)
    x = ["20\n","40\n","90\n"]
    y1 = [r[2] for r in jpeg_encode_20_862_list]
    y2 = [r[2] for r in jpeg_encode_40_862_list]
    y3 = [r[2] for r in jpeg_encode_90_862_list]
    y_720p = [np.mean(y1),np.mean(y2),np.mean(y3)]
    y1 = [r[2] for r in jpeg_encode_20_2464_list]
    y2 = [r[2] for r in jpeg_encode_40_2464_list]
    y3 = [r[2] for r in jpeg_encode_90_2464_list]
    y_2k = [np.mean(y1),np.mean(y2),np.mean(y3)]
    x_len= range(len(x))
    plt.bar(x_len, y_720p, color = 'blue', width=0.2, label='862x720')
    plt.bar([i + 0.2 for i in x_len], y_2k, color = 'green', width=0.2, label='2464x2056')
    plt.title('JPEG Compression') 
    plt.ylabel('Average Frame Size (KB)') 
    plt.xlabel('Quality') 
    plt.grid(axis="y",color='r',linestyle='--')
    plt.xticks([i + 0.1 for i in x_len], x)
    plt.ylim((0, 700))
    plt.legend()
    plt.savefig("analyze_result/ssim_size_jpeg_hevc.png", bbox_inches='tight', dpi=300)
    
    
    
