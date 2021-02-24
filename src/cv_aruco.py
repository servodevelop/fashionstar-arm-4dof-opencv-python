'''
ArucoTag检测
--------------------------------------------------
- 作者: 阿凯
- Email: kyle.xing@fashionstar.com.hk
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import numpy as np
import cv2
from cv2 import aruco

from cv_camera import Camera
from cubic_status import CubicStatus
from config import *

class ArucoDetect:
    def __init__(self, cam):
        self.cam = cam
        # 选择ArucoTag的字典
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        # 采用默认的Aruco参数
        self.aruco_params = aruco.DetectorParameters_create()
        # ArucoTag的尺寸
        self.marker_size = ARUCO_SIZE
        # 有效的ArucoID
        # self.known_arucos = [LEFT_ARUCO_ID, RIGHT_ARUCO_ID]
        self.cubic_stats = {}
        for aruco_id in ARUCO_IDS:
            self.cubic_stats[aruco_id] = CubicStatus()
        
    def find_aruco(self, img, canvas=None):
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 检测画面中的ArucoTag
        corners, aruco_ids, rejected_img_pts = aruco.detectMarkers(gray, \
            self.aruco_dict, parameters=self.aruco_params, cameraMatrix=self.cam.intrinsic, distCoeff=self.cam.distortion)

        if aruco_ids is None:
            # 画面中没有检测到ArucoTag
            return False, canvas, [], [], []

        # 获取画面中的ArucoID  
        # aruco_id = aruco_ids[0]
        # 获取旋转矩阵跟平移矩阵
        rvects, tvects, object_points = aruco.estimatePoseSingleMarkers(corners, self.marker_size, \
            self.cam.intrinsic, self.cam.distortion)
        # 将ArucoTag的tvect转换为工作台下的坐标
        
        # 可视化
        if canvas is not None:
            # 绘制Marker的边框与绘制编号
            canvas = aruco.drawDetectedMarkers(canvas, corners, aruco_ids,  (0,255,0))
            # 绘制坐标系
            n_aruco = len(tvects)
            for i in range(n_aruco):
                canvas = aruco.drawAxis(canvas, self.cam.intrinsic, \
                    self.cam.distortion, rvects[i], tvects[i], 4)

        return True, canvas, aruco_ids, rvects, tvects
    def update_cubic_stats(self, aruco_ids, rvects, tvects):
        '''更新Cubic的状态'''
        # 更新视野中没有的ArucoTag
        for aruco_id in ARUCO_IDS:
            if aruco_id not in aruco_ids:
                # 画面中没有检测到该Aruco
                self.cubic_stats[aruco_id].update(False, None)
        
        # print(tvects)
        # 更新视野中存在的ArucoTag
        # print(aruco_ids)
        for i in range(len(aruco_ids)):
            # 获取ArucoID
            aruco_id = aruco_ids[i][0]
            # 从tvec里面提取ArucoTag在工作台上的坐标
            wp_y, wp_x = tvects[i].reshape(-1)[:2]
            new_posi = (wp_x, wp_y)
            self.cubic_stats[aruco_id].update(True, new_posi)

    def display_aruco_stats(self, canvas):
        '''在画布上绘制ArucoTag的信息'''
        for aruco_id, cubic_stat in self.cubic_stats.items():
            # 画面中没有该ArucoTag
            if cubic_stat.cnt == 0:
                continue

            # 在画布上绘制ArucoTag的信息
            tag = "{}: ({:4.1f}, {:4.1f})".format(aruco_id, cubic_stat.x, cubic_stat.y)
            font = cv2.FONT_HERSHEY_SIMPLEX # 选择字体
            cv2.putText(canvas, text=tag, org=ARUCO_CANVAS_TAG_POSI[aruco_id],\
                fontFace=font, fontScale=2, thickness=4, \
                lineType=cv2.LINE_AA, color=(255, 255, 255))