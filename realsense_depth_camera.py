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
    data_format_depth = fs.getNode("data_format_depth").string().lower()
    frame_width_depth = int(fs.getNode("frame_width_depth").real())
    frame_height_depth = int(fs.getNode("frame_height_depth").real())
    frame_rate_depth = int(fs.getNode("frame_rate_depth").real())
    depth_format = getFormat(data_format_depth)
    config.enable_stream(rs.stream.depth,
                         frame_width_depth, frame_height_depth,
                         depth_format, frame_rate_depth)

    # step3 启动相机流水线
    pipeline = rs.pipeline()
    profile = pipeline.start(config)
    infra_sensor = pipeline.get_active_profile().get_device().query_sensors()[0]  # 0-depth(两个infra)相机, 1-rgb相机,2-IMU
    # 打开红外自动曝光
    infra_sensor.set_option(rs.option.enable_auto_exposure, True)
    # 打开红外发射器
    infra_sensor.set_option(rs.option.emitter_enabled, True)

    # step4 循环读取帧内容，如果需要并输出
    print("Shooting ...")
    while 1:
        frame = pipeline.wait_for_frames()
        timestamp_ms = frame.timestamp
        frame_data = np.asanyarray(frame.get_depth_frame().get_data())

        if view_mode == 1 or view_mode == 3:
            cv2.imshow("received frames", frame_data)
            cv2.waitKey(int(1))

        if view_mode == 2 or view_mode == 3:
            cv2.imwrite(output_dir_image + "/" + str(timestamp_ms) + output_type_image, frame_data)
