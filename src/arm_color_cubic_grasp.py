'''
机械臂多色色块抓取(红,黄,蓝三色)
--------------------------------------------------
- 作者: 阿凯
- Email: xingshunkai@qq.com
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import time
import cv2
from cv_camera import Camera
from cv_color_cubic import *
from fs_arm_4dof import Arm4DoF
from micro_pump import MicroPump


pump = MicroPump() # 初始化气泵
arm = Arm4DoF() # 初始化机械臂
arm.init_pose() # 机械臂初始化位姿

cam = Camera(CAM_PORT_NAME)
cam.init_camera() # 相机初始化
cam.load_cam_calib_data() # 载入图像标定数据
capture = cam.get_video_capture()

# 物块状态合计
cubic_stats = {  
    'RED': CubicStatus(),
    'YELLOW': CubicStatus(),
    'BLUE': CubicStatus()}

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

# 创建窗口
cv2.namedWindow('img_raw',flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
cv2.namedWindow('canvas',flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

while True:
    t_start = time.time()
    ret, frame = capture.read() # 获取图像
    frame = cam.remove_distortion(frame) # 移除畸变
    canvas = np.copy(frame) # 创建画布
    # 更新物块的信息
    update_cubic_stats(cam, cubic_stats, frame, canvas)
    # 在画布上打印物块在工作台上的坐标
    display_cubic_stats(cubic_stats, canvas)
    
    t_end = time.time()
    fps = 1 / (t_end - t_start)
    font = cv2.FONT_HERSHEY_SIMPLEX # 选择字体
    cv2.putText(canvas, text="fps: {:.1f}".format(fps),\
        org=(CAM_IMG_WIDTH-500, 200),\
        fontFace=font, fontScale=2, thickness=4, \
        lineType=cv2.LINE_AA, color=(0, 0, 255))

    cv2.imshow('img_raw', frame)
    cv2.imshow('canvas', canvas)
    if cv2.waitKey(1) == ord('q'):
        break
    # 移动物块
    has_mv_cubic = False
    for cname, cubic_stat in cubic_stats.items():
        # 画面中存在物块,并且位置稳定
        if cubic_stat.has_cubic() and cubic_stat.is_stable():
            cubic_posi = (cubic_stat.x, cubic_stat.y) # 色块在工作台上的坐标(2D)
            goal_posi = COLOR_CUBIC_TARGET_POSI[cname] # 色块的目标物质(3D)
            logging.info('正在搬运物块: {}'.format(cname)) 
            
            move_cubic(cubic_posi, goal_posi) # 抓取物块到目标位置
            has_mv_cubic = True

    # 清空摄像头缓冲
    if has_mv_cubic:
        cam.empty_cache()

capture.release()
cv2.destroyAllWindows()
