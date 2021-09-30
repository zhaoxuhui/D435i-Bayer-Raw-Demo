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
    enable_AE_infra = int(fs.getNode("enable_AE_infra").real())
    enable_emitter = int(fs.getNode("enable_emitter").real())
    infra_mode = int(fs.getNode("infra_mode").real())
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
    data_format_infra = fs.getNode("data_format_infra").string().lower()
    frame_width_infra = int(fs.getNode("frame_width_infra").real())
    frame_height_infra = int(fs.getNode("frame_height_infra").real())
    frame_rate_infra = int(fs.getNode("frame_rate_infra").real())
    infra_format = getFormat(data_format_infra)
    if infra_mode == 1:
        config.enable_stream(rs.stream.infrared, 1,
                             frame_width_infra, frame_height_infra,
                             infra_format, frame_rate_infra)
    elif infra_mode == 2:
        config.enable_stream(rs.stream.infrared, 2,
                             frame_width_infra, frame_height_infra,
                             infra_format, frame_rate_infra)
    elif infra_mode == 3:
        config.enable_stream(rs.stream.infrared, 1,
                             frame_width_infra, frame_height_infra,
                             infra_format, frame_rate_infra)
        config.enable_stream(rs.stream.infrared, 2,
                             frame_width_infra, frame_height_infra,
                             infra_format, frame_rate_infra)

    # step3 启动相机流水线并设置是否自动曝光
    pipeline = rs.pipeline()
    profile = pipeline.start(config)
    infra_sensor = pipeline.get_active_profile().get_device().query_sensors()[0]  # 0-depth(两个infra)相机, 1-rgb相机,2-IMU
    # 自动曝光设置
    if enable_AE_infra == 1:
        infra_sensor.set_option(rs.option.enable_auto_exposure, True)
    else:
        manual_exposure_color = fs.getNode("manual_exposure_color").real()
        infra_sensor.set_option(rs.option.exposure, manual_exposure_color)
    # 红外发射器设置
    if enable_emitter == 1:
        infra_sensor.set_option(rs.option.emitter_enabled, True)
    else:
        infra_sensor.set_option(rs.option.emitter_enabled, False)

    # step4 循环读取帧内容，如果需要并输出
    print("Shooting ...")
    while 1:
        frame = pipeline.wait_for_frames()
        timestamp_ms = frame.timestamp
        if infra_mode != 3:
            frame_data = np.asanyarray(frame.get_infrared_frame().get_data())

            if view_mode == 1 or view_mode == 3:
                cv2.imshow("received frames", frame_data)
                cv2.waitKey(int(1))

            if view_mode == 2 or view_mode == 3:
                cv2.imwrite(output_dir_image + "/" + str(timestamp_ms) + output_type_image, frame_data)
        else:
            left_frame_data = np.asanyarray(frame.get_infrared_frame(1).get_data())
            right_frame_data = np.asanyarray(frame.get_infrared_frame(2).get_data())

            if view_mode == 1 or view_mode == 3:
                cv2.namedWindow("left infra")
                cv2.namedWindow("right infra")
                cv2.imshow("left infra", left_frame_data)
                cv2.imshow("right infra", right_frame_data)
                cv2.waitKey(int(1))

            if view_mode == 2 or view_mode == 3:
                cv2.imwrite(output_dir_image + "/" + str(timestamp_ms) + "_left" + output_type_image, left_frame_data)
                cv2.imwrite(output_dir_image + "/" + str(timestamp_ms) + "_right" + output_type_image, right_frame_data)
