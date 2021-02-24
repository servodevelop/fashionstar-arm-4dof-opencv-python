'''
测试ArucoTag检测与测量
--------------------------------------------------
- 作者: 阿凯
- Email: kyle.xing@fashionstar.com.hk
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import logging
import sys
from absl import app
from absl import flags

import numpy as np
import cv2
from cv2 import aruco

from cv_camera import Camera
from cv_aruco import ArucoDetect
from config import *

def main(argv):
    # 创建相机对象
    cam = Camera(FLAGS.device)
    # 初始相机
    cam.init_camera()
    capture = cam.get_video_capture()
    # 载入标定数据
    cam.load_cam_calib_data()
    # 载入透视逆变换矩阵
    # cam.load_ipm_remap(calc_online=False)
    # 图像预处理窗口
    cv2.namedWindow('aruco',flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    # 创建ArucoTag检测器
    aruco_detect = ArucoDetect(cam)
    while True:
        ret, frame = capture.read()
        # find_aruco函数内部就会去除畸变
        # frame = cam.remove_distortion(frame) # 移除畸变
        canvas = np.copy(frame)
        # ArucoTag检测
        has_aruco, canvas, aruco_ids, rvects, tvects = aruco_detect.find_aruco(frame, canvas=canvas)
        # 更新ArucoTag的状态
        aruco_detect.update_cubic_stats(aruco_ids, rvects, tvects)
        # 显示ArucoTag的位置信息
        aruco_detect.display_aruco_stats(canvas)

        cv2.imshow('aruco', canvas)
        key = cv2.waitKey(1)
        if key == ord('q'):
            # 如果按键为q 代表quit 退出程序
            break  
        elif key == ord('s'):
            # s键代表保存数据
            cv2.imwrite('{}/{}.png'.format(FLAGS.img_path, img_cnt), canvas)
            logging.info("截图，并保存在  {}/{}.png".format(FLAGS.img_path, img_cnt))
            img_cnt += 1

if __name__ == '__main__':         
    # 设置日志等
    logging.basicConfig(level=logging.INFO)
    # 定义参数
    FLAGS = flags.FLAGS
    flags.DEFINE_string('device', '/dev/video0', '摄像头的设备号')
    flags.DEFINE_integer('img_cnt', 0, '图像计数的起始数值')
    flags.DEFINE_string('img_path', 'data/img_with_aruco', '图像的保存地址')
    app.run(main)