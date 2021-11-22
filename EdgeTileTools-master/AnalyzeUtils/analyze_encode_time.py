from matplotlib import pyplot as plt
import numpy as np
# 该文件用于分析pc上和ios上kvazaar的编码（hevc）效率
if __name__ == "__main__":
    encoder_time_list_on_pc_2k = []
    encoder_time_list_on_iphone_2k = []
    encoder_time_list_on_pc_720p = []
    encoder_time_list_on_iphone_720p = []

    with open('encoder_time_logs/encoder_time_pc_2k.log', 'r', encoding='utf-8') as f:
        for line in f:
            frame, encode_time = int(line.split(
                ',')[0]), int(line.split(',')[1])
            encoder_time_list_on_pc_2k.append((frame, encode_time))
    with open('encoder_time_logs/encoder_time_ios_2k.log', 'r', encoding='utf-8') as f:
        for line in f:
            frame, encode_time = int(line.split(
                ',')[0]), int(line.split(',')[1])
            encoder_time_list_on_iphone_2k.append((frame, encode_time))
    with open('encoder_time_logs/encoder_time_pc_720p.log', 'r', encoding='utf-8') as f:
        for line in f:
            frame, encode_time = int(line.split(
                ',')[0]), int(line.split(',')[1])
            encoder_time_list_on_pc_720p.append((frame, encode_time))
    with open('encoder_time_logs/encoder_time_ios_720p.log', 'r', encoding='utf-8') as f:
        for line in f:
            frame, encode_time = int(line.split(
                ',')[0]), int(line.split(',')[1])
            encoder_time_list_on_iphone_720p.append((frame, encode_time))

    plt.figure(figsize=(30, 20))

    plt.subplot(2,  3,  1)
    x = [r[0] for r in encoder_time_list_on_pc_2k]
    y = [r[1] for r in encoder_time_list_on_pc_2k]
    plt.plot(x, y, color="green", marker='o', linestyle='-')
    plt.title('Encoder Efficiency on PC(2k)\n(ave_encode_time:{:.2f} ms)'.format(
        np.mean(y)), fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("Encode Time Cost(ms)")

    plt.subplot(2,  3,  2)
    x = [r[0] for r in encoder_time_list_on_iphone_2k]
    y = [r[1] for r in encoder_time_list_on_iphone_2k]
    plt.plot(x, y, color="blue", marker='.', linestyle='-')
    plt.title('Encoder Efficiency on IPhone(2k)\n(ave_encode_time:{:.2f} ms)'.format(
        np.mean(y)), fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("Encode Time Cost(ms)")

    plt.subplot(2,  3,  3)
    x1 = [r[0] for r in encoder_time_list_on_pc_2k]
    y1 = [r[1] for r in encoder_time_list_on_pc_2k]
    plt.plot(x1, y1, color="green", marker='o', linestyle='-', label='on PC')
    plt.hlines(np.mean(y1), 0, 200, colors="green", linestyles="dashed")
    x2 = [r[0] for r in encoder_time_list_on_iphone_2k]
    y2 = [r[1] for r in encoder_time_list_on_iphone_2k]
    plt.plot(x2, y2, color="blue", marker='.',
             linestyle='-', label='on IPhone')
    plt.hlines(np.mean(y2), 0, 200, colors="blue", linestyles="dashed")
    plt.title('Encoder Efficiency(2k)', fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("Encode Time Cost(ms)")
    plt.legend()

    plt.subplot(2,  3,  4)
    x = [r[0] for r in encoder_time_list_on_pc_720p]
    y = [r[1] for r in encoder_time_list_on_pc_720p]
    plt.plot(x, y, color="green", linestyle='-')
    plt.title('Encoder Efficiency on PC(720p)\n(ave_encode_time:{:.2f} ms)'.format(
        np.mean(y)), fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("Encode Time Cost(ms)")

    plt.subplot(2,  3,  5)
    x = [r[0] for r in encoder_time_list_on_iphone_720p]
    y = [r[1] for r in encoder_time_list_on_iphone_720p]
    plt.plot(x, y, color="blue", linestyle='-')
    plt.title('Encoder Efficiency on IPhone(720p)\n(ave_encode_time:{:.2f} ms)'.format(
        np.mean(y)), fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("Encode Time Cost(ms)")

    plt.subplot(2,  3,  6)
    x1 = [r[0] for r in encoder_time_list_on_pc_720p]
    y1 = [r[1] for r in encoder_time_list_on_pc_720p]
    plt.plot(x1, y1, color="green", linestyle='-', label='on PC')
    plt.hlines(np.mean(y1), 0, 200, colors="green", linestyles="dashed")
    x2 = [r[0] for r in encoder_time_list_on_iphone_720p]
    y2 = [r[1] for r in encoder_time_list_on_iphone_720p]
    plt.plot(x2, y2, color="blue", linestyle='-', label='on IPhone')
    plt.hlines(np.mean(y2), 0, 200, colors="blue", linestyles="dashed")
    plt.title('Encoder Efficiency(720p)', fontsize=12)
    plt.xlabel("Frame")
    plt.ylabel("Encode Time Cost(ms)")
    plt.legend()

    plt.savefig("result_encode_time.png", bbox_inches='tight', dpi=300)
    
    plt.close('all') # 清空，重新画
    plt.figure(figsize=(5, 3))
    x = ['720p', '2k']
    y1 = [r[1] for r in encoder_time_list_on_pc_720p]
    y2 = [r[1] for r in encoder_time_list_on_pc_2k]
    y_pc = [np.mean(y1),np.mean(y2)]
    y1 = [r[1] for r in encoder_time_list_on_iphone_720p]
    y2 = [r[1] for r in encoder_time_list_on_iphone_2k]
    y_iphone = [np.mean(y1),np.mean(y2)]
    x_len= range(len(x))
    plt.bar(x_len, y_pc, color = 'blue', width=0.2, label='on pc')
    plt.bar([i + 0.2 for i in x_len], y_iphone, color = 'green', width=0.2, label='on iphone')
    plt.title('Encoder Efficiency') 
    plt.ylabel('Average Encode Time Cost(ms)') 
    plt.xlabel('Resolution') 
    plt.grid(axis="y",color='r',linestyle='--')
    plt.xticks([i + 0.1 for i in x_len], x)
    # plt.ylim((0, 900))
    plt.legend()
 
    plt.savefig("result_encode_time_hevc.png", bbox_inches='tight', dpi=300)

    # plt.show()
