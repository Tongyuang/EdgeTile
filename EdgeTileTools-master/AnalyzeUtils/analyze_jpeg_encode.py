from matplotlib import pyplot as plt
import numpy as np
# 该文件用于分析ios上jpeg的编码效率(1280*720,3840*2160)
if __name__ == "__main__":
    jpeg_encode_20_720_list = []
    jpeg_encode_50_720_list = []
    jpeg_encode_80_720_list = []
    jpeg_encode_100_720_list = []
    

    jpeg_encode_20_2160_list = []
    jpeg_encode_50_2160_list = []
    jpeg_encode_80_2160_list = []
    jpeg_encode_100_2160_list = []

    hevc_encoder_time_list_on_iphone_720p = []
    hevc_encoder_time_list_on_iphone_2k = []
    names = locals()

    with open('encoder_time_logs/encoder_time_ios_720p.log', 'r', encoding='utf-8') as f:
        for line in f:
            frame, encode_time = int(line.split(
                ',')[0]), int(line.split(',')[1])
            hevc_encoder_time_list_on_iphone_720p.append((frame, encode_time))

    with open('encoder_time_logs/encoder_time_ios_2k.log', 'r', encoding='utf-8') as f:
        for line in f:
            frame, encode_time = int(line.split(
                ',')[0]), int(line.split(',')[1])
            hevc_encoder_time_list_on_iphone_2k.append((frame, encode_time))
    
    
    for quality in [20, 50, 80, 100]:
        for resolution in [720, 2160]:
            with open('jpeg_encode_logs/jpeg_encode_{}_{}.log'.format(quality, resolution), 'r', encoding='utf-8') as f:
                for line in f:
                    frame, encode_time, img_size = int(line.split(
                        ',')[0]), int(line.split(',')[1]),int(int(line.split(',')[2])/1000)
                    names['jpeg_encode_{}_{}_list'.format(quality, resolution)].append((frame, encode_time,img_size))
    # 图1 
    plt.figure(figsize=(15, 10))

    plt.subplot(2,  2,  1)
    x1 = [r[0] for r in jpeg_encode_20_720_list]
    y1 = [r[1] for r in jpeg_encode_20_720_list]
    plt.plot(x1, y1, color="blue", linestyle='-', label='quality=20')
    x2 = [r[0] for r in jpeg_encode_50_720_list]
    y2 = [r[1] for r in jpeg_encode_50_720_list]
    plt.plot(x2, y2, color="red", linestyle='-', label='quality=50')
    x3 = [r[0] for r in jpeg_encode_80_720_list]
    y3 = [r[1] for r in jpeg_encode_80_720_list]
    plt.plot(x3, y3, color="green", linestyle='-', label='quality=80')
    x4 = [r[0] for r in jpeg_encode_100_720_list]
    y4 = [r[1] for r in jpeg_encode_100_720_list]
    plt.plot(x4, y4, color="black", linestyle='-', label='quality=100')
    y1_mean = np.mean(y1)
    y2_mean = np.mean(y2)
    y3_mean = np.mean(y3)
    y4_mean = np.mean(y4)
    print("Encode Time Cost(ms) on 720p:")
    print("quality = 20: {}".format(y1_mean))
    print("quality = 50: {}".format(y2_mean))
    print("quality = 80: {}".format(y3_mean))
    print("quality = 100: {}".format(y4_mean))
    plt.title('Encoder Efficiency(720p)', fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("Encode Time Cost(ms)")
    plt.legend()

    plt.subplot(2,  2,  2)
    x1 = [r[0] for r in jpeg_encode_20_2160_list]
    y1 = [r[1] for r in jpeg_encode_20_2160_list]
    plt.plot(x1, y1, color="blue", linestyle='-', label='quality=20')
    x2 = [r[0] for r in jpeg_encode_50_2160_list]
    y2 = [r[1] for r in jpeg_encode_50_2160_list]
    plt.plot(x2, y2, color="red", linestyle='-', label='quality=50')
    x3 = [r[0] for r in jpeg_encode_80_2160_list]
    y3 = [r[1] for r in jpeg_encode_80_2160_list]
    plt.plot(x3, y3, color="green", linestyle='-', label='quality=80')
    x4 = [r[0] for r in jpeg_encode_100_2160_list]
    y4 = [r[1] for r in jpeg_encode_100_2160_list]
    plt.plot(x4, y4, color="black", linestyle='-', label='quality=100')
    y1_mean = np.mean(y1)
    y2_mean = np.mean(y2)
    y3_mean = np.mean(y3)
    y4_mean = np.mean(y4)
    print("Encode Time Cost(ms) on 2k:")
    print("quality = 20: {}".format(y1_mean))
    print("quality = 50: {}".format(y2_mean))
    print("quality = 80: {}".format(y3_mean))
    print("quality = 100: {}".format(y4_mean))
    plt.title('Encoder Efficiency(2k)', fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("Encode Time Cost(ms)")
    plt.legend()

    plt.subplot(2,  2,  3)
    x1 = [r[0] for r in jpeg_encode_20_720_list]
    y1 = [r[2] for r in jpeg_encode_20_720_list]
    plt.plot(x1, y1, color="blue", linestyle='-', label='quality=20')
    x2 = [r[0] for r in jpeg_encode_50_720_list]
    y2 = [r[2] for r in jpeg_encode_50_720_list]
    plt.plot(x2, y2, color="red", linestyle='-', label='quality=50')
    x3 = [r[0] for r in jpeg_encode_80_720_list]
    y3 = [r[2] for r in jpeg_encode_80_720_list]
    plt.plot(x3, y3, color="green", linestyle='-', label='quality=80')
    x4 = [r[0] for r in jpeg_encode_100_720_list]
    y4 = [r[2] for r in jpeg_encode_100_720_list]
    plt.plot(x4, y4, color="black", linestyle='-', label='quality=100')
    y1_mean = np.mean(y1)
    y2_mean = np.mean(y2)
    y3_mean = np.mean(y3)
    y4_mean = np.mean(y4)
    print("Encoded JPEG size(KB) on 720p:")
    print("quality = 20: {}".format(y1_mean))
    print("quality = 50: {}".format(y2_mean))
    print("quality = 80: {}".format(y3_mean))
    print("quality = 100: {}".format(y4_mean))
    plt.title('Encoded JPEG size(720p)', fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("JPEG size(KB)")
    plt.legend()

    plt.subplot(2,  2,  4)
    x1 = [r[0] for r in jpeg_encode_20_2160_list]
    y1 = [r[2] for r in jpeg_encode_20_2160_list]
    plt.plot(x1, y1, color="blue", linestyle='-', label='quality=20')
    x2 = [r[0] for r in jpeg_encode_50_2160_list]
    y2 = [r[2] for r in jpeg_encode_50_2160_list]
    plt.plot(x2, y2, color="red", linestyle='-', label='quality=50')
    x3 = [r[0] for r in jpeg_encode_80_2160_list]
    y3 = [r[2] for r in jpeg_encode_80_2160_list]
    plt.plot(x3, y3, color="green", linestyle='-', label='quality=80')
    x4 = [r[0] for r in jpeg_encode_100_2160_list]
    y4 = [r[2] for r in jpeg_encode_100_2160_list]
    plt.plot(x4, y4, color="black", linestyle='-', label='quality=100')
    y1_mean = np.mean(y1)
    y2_mean = np.mean(y2)
    y3_mean = np.mean(y3)
    y4_mean = np.mean(y4)
    print("Encoded JPEG size(KB) on 2k:")
    print("quality = 20: {}".format(y1_mean))
    print("quality = 50: {}".format(y2_mean))
    print("quality = 80: {}".format(y3_mean))
    print("quality = 100: {}".format(y4_mean))
    plt.title('Encoded JPEG size(2k)', fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("JPEG size(KB)")
    plt.legend()

    plt.savefig("result_jpeg_encode_1.png", bbox_inches='tight', dpi=300)
    plt.close('all') # 清空，重新画

    # 图2
    plt.figure(figsize=(15, 10))
    x = ["20", "50", "80", "100"]
    y1 = [r[2] for r in jpeg_encode_20_720_list]
    y2 = [r[2] for r in jpeg_encode_50_720_list]
    y3 = [r[2] for r in jpeg_encode_80_720_list]
    y4 = [r[2] for r in jpeg_encode_100_720_list]
    y_720p = [np.mean(y1),np.mean(y2), np.mean(y3), np.mean(y4)]
    y1 = [r[2] for r in jpeg_encode_20_2160_list]
    y2 = [r[2] for r in jpeg_encode_50_2160_list]
    y3 = [r[2] for r in jpeg_encode_80_2160_list]
    y4 = [r[2] for r in jpeg_encode_100_2160_list]
    y_2k = [np.mean(y1),np.mean(y2), np.mean(y3), np.mean(y4)]
    x_len= range(len(x))
    plt.bar(x_len, y_720p, color = 'blue', width=0.2, label='1280x720')
    plt.bar([i + 0.2 for i in x_len], y_2k, color = 'green', width=0.2, label='3840x2160')
    plt.title('JPEG Compression') 
    plt.ylabel('Average Frame Size (KB)') 
    plt.xlabel('Quality') 
    plt.grid(axis="y",color='r',linestyle='--')
    plt.xticks([i + 0.1 for i in x_len], x)
    plt.ylim((0, 900))
    plt.legend()

    plt.savefig("result_jpeg_encode_2.png", bbox_inches='tight', dpi=300)
    plt.close('all') # 清空，重新画

    # 图3
    plt.figure(figsize=(6, 3))
    x = ['720p', '2k']
    y1 = [r[1] for r in jpeg_encode_80_720_list]
    y2 = [r[1] for r in jpeg_encode_80_2160_list]
    y_720p = [np.mean(y1),np.mean(y2)]
    y1 = [r[1] for r in hevc_encoder_time_list_on_iphone_720p]
    y2 = [r[1] for r in hevc_encoder_time_list_on_iphone_2k]
    y_2k = [np.mean(y1),np.mean(y2)]
    x_len= range(len(x))
    plt.bar(x_len, y_720p, color = 'blue', width=0.2, label='jpeg encode')
    plt.bar([i + 0.2 for i in x_len], y_2k, color = 'green', width=0.2, label='hevc encode')
    plt.title('Encoder Efficiency')
    plt.ylabel('Average Encode Time Cost(ms)') 
    plt.xlabel('Resolution') 
    plt.grid(axis="y",color='r',linestyle='--')
    plt.xticks([i + 0.1 for i in x_len], x)
    plt.legend()
    plt.savefig("result_jpeg_encode_3.png", bbox_inches='tight', dpi=300)


    
