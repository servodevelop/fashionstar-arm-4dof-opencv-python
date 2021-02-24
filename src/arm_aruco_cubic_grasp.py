'''
机械臂ArucoTag识别与抓取
--------------------------------------------------
- 作者: 阿凯
- Email: kyle.xing@fashionstar.com.hk
- 更新时间: 2020-03-14
--------------------------------------------------
'''
import logging
import sys
from absl import app
from absl import flags

import numpy as np
import cv2

from cv_camera import Camera
from cv_aruco import ArucoDetect
from fs_arm_4dof import Arm4DoF
from micro_pump import MicroPump
from config import *

pump = MicroPump() # 初始化气泵
arm = Arm4DoF() # 初始化机械臂
arm.init_pose() # 机械臂初始化位姿

def tf_ws2arm(wx:float, wy:float, wz:float=0):
    '''工作台坐标系到机器人基坐标系下的转换'''
    ofx, ofy, ofz = WORKSPACE_ORIGIN_POSI
    return [wx + ofx, wy+ofy, wz+ofz]

def move_cubic(cubic_posi:tuple, goal_posi:tuple):
    '''移动物块的动作组'''
    global arm
    global pump
    wx, wy = cubic_posi
    tool_posi = tf_ws2arm(wx, wy) # 将工作台坐标系转换为机械基坐标系
    x1, y1, z1 = tool_posi
    x2, y2, z2 = goal_posi
    # 运动到物体的上方
    arm.move2([x1, y1, z1+4], 1)
    # 气泵下压
    arm.move2([x1, y1, z1-1], 1)
    # 气泵吸气
    pump.on()
    # 再次抬起
    arm.move2([x1, y1, z1+4], 1)
    # 搬运到目的地
    arm.move2([x2, y2, z2], 1)
    # 气泵放气
    pump.off()

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
        
        for aruco_id, cubic_stat in aruco_detect.cubic_stats.items():
            # 画面中存在物块,并且位置稳定
            if cubic_stat.has_cubic() and cubic_stat.is_stable():
                cubic_posi = (cubic_stat.x, cubic_stat.y) # 色块在工作台上的坐标(2D)
                goal_posi = ARUCO_CUBIC_TARGET_POSI[aruco_id] # 色块的目标物质(3D)
                logging.info('正在搬运物块 ArucoTag ID = {}'.format(aruco_id)) 
                move_cubic(cubic_posi, goal_posi) # 抓取物块到目标位置
        cam.empty_cache()

if __name__ == '__main__':         
    # 设置日志等
    logging.basicConfig(level=logging.INFO)
    # 定义参数
    FLAGS = flags.FLAGS
    flags.DEFINE_string('device', '/dev/video0', '摄像头的设备号')
    flags.DEFINE_integer('img_cnt', 0, '图像计数的起始数值')
    flags.DEFINE_string('img_path', 'data/img_with_aruco', '图像的保存地址')
    app.run(main)
