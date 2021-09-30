import pyrealsense2 as rs
import numpy as np
import cv2

if __name__ == '__main__':
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
    config.enable_stream(rs.stream.color,
                         1920, 1080,
                         rs.format.raw16, 30)

    # step3 启动相机流水线并设置是否自动曝光
    pipeline = rs.pipeline()
    profile = pipeline.start(config)
    color_sensor = pipeline.get_active_profile().get_device().query_sensors()[1]  # 0-depth(两个infra)相机, 1-rgb相机,2-IMU
    # 自动曝光设置
    color_sensor.set_option(rs.option.enable_auto_exposure, True)

    # step4 循环读取帧内容，如果需要并输出
    print("Shooting ...")
    while 1:
        frame = pipeline.wait_for_frames()
        frame_data = np.asanyarray(frame.get_color_frame().get_data())
        timestamp_ms = frame.timestamp

        cv2.imshow("received frames", frame_data)
        cv2.waitKey(int(1))
