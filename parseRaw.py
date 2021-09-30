import cv2
import numpy as np

if __name__ == '__main__':
    file_path = "./test_raw.png"

    # step1 读取数据
    # ----------------------------------------------------------------------------------
    raw_data = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    # ----------------------------------------------------------------------------------

    # step2 Bayer插值
    # ----------------------------------------------------------------------------------
    # Bayer array:
    # G     B
    # R     G
    raw_data_bgr = cv2.cvtColor(raw_data, cv2.COLOR_BAYER_GB2BGR)
    print('image size:', raw_data_bgr.shape)
    # ----------------------------------------------------------------------------------

    # step3 白平衡
    # ----------------------------------------------------------------------------------
    band_b = raw_data_bgr[:, :, 0]
    band_g = raw_data_bgr[:, :, 1]
    band_r = raw_data_bgr[:, :, 2]

    band_r = band_r * 2.04
    band_g = band_g
    band_b = band_b * 1.32
    # ----------------------------------------------------------------------------------

    # step4 缩放颜色尺度
    # ----------------------------------------------------------------------------------
    max_r = np.max(band_r)
    max_g = np.max(band_g)
    max_b = np.max(band_b)
    print('max red:', max_r, 'max green:', max_g, 'max blue:', max_b)
    min_value = min(max_r, min(max_g, max_b))
    print('min value:', min_value)

    band_r_clip = np.where(band_r > min_value, min_value, band_r)
    band_g_clip = np.where(band_g > min_value, min_value, band_g)
    band_b_clip = np.where(band_b > min_value, min_value, band_b)
    # ----------------------------------------------------------------------------------

    # step5 合并波段并输出
    # ----------------------------------------------------------------------------------
    band_r_clip_int = np.zeros([band_r_clip.shape[0], band_r_clip.shape[1]], np.uint8)
    band_g_clip_int = np.zeros([band_g_clip.shape[0], band_g_clip.shape[1]], np.uint8)
    band_b_clip_int = np.zeros([band_b_clip.shape[0], band_b_clip.shape[1]], np.uint8)

    for i in range(band_r_clip.shape[0]):
        for j in range(band_r_clip_int.shape[1]):
            band_r_clip_int[i, j] = int(band_r_clip[i, j] / 256)
            band_g_clip_int[i, j] = int(band_g_clip[i, j] / 256)
            band_b_clip_int[i, j] = int(band_b_clip[i, j] / 256)

    bands = cv2.merge((band_b_clip_int, band_g_clip_int, band_r_clip_int))

    cv2.imwrite("merged.png", bands)
    # ----------------------------------------------------------------------------------
