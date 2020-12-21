'''
机械臂单色色块抓取(只识别并抓取红色色块)
--------------------------------------------------
- 作者: 阿凯
- Email: xingshunkai@qq.com
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import time
import cv2
import logging

from fs_arm_4dof import Arm4DoF
from micro_pump import MicroPump
from cv_camera import Camera
from cv_color_cubic import *
from cubic_status import CubicStatus
from config import *

pump = MicroPump()
arm = Arm4DoF()
arm.init_pose() 
red_cubic_stat = CubicStatus() # 物块的状态信息

def detect_red_cubic(canvas:np.array):
    '''红色色块测量'''
    global red_cubic_stat
    ret1,result1 = find_cubic_contour(frame, RED_BLOCK_LOWERB, RED_BLOCK_UPPERB, canvas=canvas)
    if ret1:
        (cubic_rect,contour) = result1
        # 计算重投影之后的点
        ret2,result2 = get_cubic_corner(contour, canvas=canvas, blob_color=(0, 0, 255))
        if ret2:
            A2, B2, C2, D2, O = result2
            cubic_img_pts = [A2, B2, C2, D2]
            rvec, tvec = cubic_pose_estimate(cam, cubic_img_pts, canvas=canvas)
            x, y, z = [float(v) for v in tvec.reshape(-1)]
            
            # 将平移向量tvec,　变换为工作台的xy坐标
            wp_y, wp_x = tvec.reshape(-1)[:2]
            # 新的位置
            new_posi = (wp_x, wp_y)
            red_cubic_stat.update(True, new_posi)
            # 绘制红色色块在工作台上的坐标
            tag = "red: x={:4.1f}, y={:4.1f}".format(red_cubic_stat.x, red_cubic_stat.y)
            font = cv2.FONT_HERSHEY_SIMPLEX # 选择字体
            cv2.putText(canvas, text=tag, org=(20, 200), fontFace=font, fontScale=2, \
                thickness=4, lineType=cv2.LINE_AA, color=(0, 0, 255))

            if red_cubic_stat.is_stable():
                print("红色物块稳定, 可以抓取啦")
                # print('x:{} y:{}'.format(red_cubic_stat.x, red_cubic_stat.y))
            return True, new_posi

    red_cubic_stat.update(False, None)
    return False, None

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
    
def grab_red_block(red_cubic_stat:CubicStatus):
    '''抓取红色的色块'''
    cubic_posi = (red_cubic_stat.x, red_cubic_stat.y) # 物块的位置
    goal_posi = (1, 15, 0)
    move_cubic(cubic_posi, goal_posi)
    red_cubic_stat.reset()
    
# 创建窗口
cv2.namedWindow('img_raw',flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
cv2.namedWindow('canvas',flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

# 从视频流里面获取图像并进行色块角点识别
cam = Camera(CAM_PORT_NAME)
cam.init_camera()
cam.load_cam_calib_data() # 载入图像标定数据
capture = cam.get_video_capture()

while True:
    ret, frame = capture.read() # 获取图像
    frame = cam.remove_distortion(frame) # 移除畸变
    canvas = np.copy(frame) # 创建画布
    detect_red_cubic(canvas) # 检测红色色块
    
    cv2.imshow('img_raw', frame)
    cv2.imshow('canvas', canvas)
    if cv2.waitKey(1) == ord('q'):
        break
        
    if red_cubic_stat.is_stable():
        grab_red_block(red_cubic_stat)
        for i in range(5):
            ret, frame = capture.read()

capture.release()
cv2.destroyAllWindows()
