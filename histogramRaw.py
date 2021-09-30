from matplotlib import pyplot as plt  # 可视化相关
import cv2

if __name__ == '__main__':
    raw_data = cv2.imread("test_raw.png", cv2.IMREAD_UNCHANGED)

    # 遍历像素统计灰度直方图
    bins = [0] * 65535
    for i in range(raw_data.shape[0]):
        # print(i + 1, '/', raw_data.shape[0])
        for j in range(raw_data.shape[1]):
            bins[int(raw_data[i, j])] += 1

    # 435i的Raw数据是16bit，但并非是真正的16bit，而是10bit数据拉伸后(乘以64)得到的
    bins_compressed = [9] * 1024
    for i in range(0, len(bins), 64):
        bins_compressed[int(i / 64)] = bins[i]

    for i in range(len(bins_compressed)):
        print(i, '\t', bins_compressed[i])

    # 绘制灰度直方图
    plt.figure(1)
    plt.bar(range(len(bins_compressed)), bins_compressed)

    plt.show()
