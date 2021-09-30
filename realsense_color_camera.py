import pyrealsense2 as rs
import numpy as np
import cv2
import os


def getFormat(data_format):
    format = rs.format.rgb8
    if data_format.__contains__("rgb8"):
        format = rs.format.rgb8
    elif data_format.__contains__("bgr8"):
        format = rs.format.bgr8
    elif data_format.__contains__("raw8"):
        format = rs.format.raw8
    elif data_format.__contains__("raw10"):
        format = rs.format.raw10
    elif data_format.__contains__("raw16"):
        format = rs.format.raw16
    elif data_format.__contains__("y8"):
        format = rs.format.y8
    elif data_format.__contains__("y16"):
        format = rs.format.y16
    elif data_format.__contains__("z16"):
        format = rs.format.z16
    elif data_format.__contains__("yuyv"):
        format = rs.format.yuyv
    elif data_format.__contains__("xyz32f"):
        format = rs.format.motion_xyz32f
    return format


def isDirExist(path='output'):
    """
    判断指定目录是否存在，如果存在返回True，否则返回False并新建目录

    :param path: 指定目录
    :return: 判断结果

    """

    if not os.path.exists(path):
        os.makedirs(path)
        return False
    else:
        return True


if __name__ == '__main__':
    config_file = "config.yml"
    fs = cv2.FileStorage(config_file, cv2.FILE_STORAGE_READ)

    # step0 一些运行前零碎操作
    view_mode = int(fs.getNode("view_mode").real())
    enable_AE_color = int(fs.getNode("enable_AE_color").real())
    if view_mode == 2 or view_mode == 3:
        output_dir_image = fs.getNode("output_dir_image").string().lower()
        output_type_image = fs.getNode("output_type_image").string().lower()
        isDirExist(output_dir_image)
        if not output_type_image.startswith("."):
            output_type_image = "." + output_type_image

    # step1 检查并初始化设备可用性
    ctx = rs.context()
    if len(ctx.devices) == 0:
        print("No realsense D435i was detected.")
        exit()
    device = ctx.devices[0]
    serial_number = device.get_info(rs.camera_info.serial_number)
    config = rs.config()
    config.enable_device(serial_number)

    # step2 根据配置文件设置数据流
    data_format_color = fs.getNode("data_format_color").string().lower()
    frame_width_color = int(fs.getNode("frame_width_color").real())
    frame_height_color = int(fs.getNode("frame_height_color").real())
    frame_rate_color = int(fs.getNode("frame_rate_color").real())
    color_format = getFormat(data_format_color)
    config.enable_stream(rs.stream.color,
                         frame_width_color, frame_height_color,
                         color_format, frame_rate_color)

    # step3 启动相机流水线并设置是否自动曝光
    pipeline = rs.pipeline()
    profile = pipeline.start(config)
    color_sensor = pipeline.get_active_profile().get_device().query_sensors()[1]  # 0-depth(两个infra)相机, 1-rgb相机,2-IMU
    # 自动曝光设置
    if enable_AE_color == 1:
        color_sensor.set_option(rs.option.enable_auto_exposure, True)
    else:
        manual_exposure_color = fs.getNode("manual_exposure_color").real()
        color_sensor.set_option(rs.option.exposure, manual_exposure_color)

    # step4 循环读取帧内容，如果需要并输出
    print("Shooting ...")
    while 1:
        frame = pipeline.wait_for_frames()
        frame_data = np.asanyarray(frame.get_color_frame().get_data())
        timestamp_ms = frame.timestamp

        if data_format_color.__contains__("rgb"):
            frame_data = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)

        if view_mode == 1 or view_mode == 3:
            cv2.imshow("received frames", frame_data)
            cv2.waitKey(int(1))

        if view_mode == 2 or view_mode == 3:
            cv2.imwrite(output_dir_image + "/" + str(timestamp_ms) + output_type_image, frame_data)
