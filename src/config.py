'''
Fashion Star 4DoF机械臂的配置文件与视觉识别的配置文件
--------------------------------------------------
- 作者: 阿凯
- Email: kyle.xing@fashionstar.com.hk
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import math
#############################
## 树莓派版本号
##
#############################
RASP_VERSION = 4

##########################################
## 机械臂-设备
##
##########################################
# 串口舵机的默认设备号

DEVICE_PORT_DEFAULT = '/dev/ttyUSB0' # RaspberryPi4
# DEVICE_PORT_DEFAULT = '/dev/ttyS0' # RaspberryPi4
# DEVICE_PORT_DEFAULT = 'COM3' # PC Windows
# DEVICE_PORT_DEFAULT = '/dev/ttyUSB0' # PC Ubuntu

##########################################
## 微型气泵与电磁阀
## 适用于FashionStar树莓派串口总线舵机拓展版
##########################################
MICRO_PUMP_SWITCH = False # True # False
GPIO_PUMP_MOTOR = 7 # 微型气泵马达在拓展板上的GPIO
GPIO_MAGNETIC_SWITCH = 16 # 电磁阀开关的GPIO

##########################################
## 串口舵机参数
##
##########################################
SERVO_NUM = 4 # 舵机的个数
SERVO_SPEED_DEFAULT = 100 # 舵机默认的平均转速 °/s
SERVO_SPEED_MIN = 1 # 转速的最大值
SERVO_SPEED_MAX = 200 # 转速的最小值

##########################################
## 机械臂-连杆参数
## 单位cm
##########################################
LINK23 = 8.1    # JOINT2与JOINT3(腕关节)的长度
LINK34 = 7.8    # JOINT3与JOINT4(腕关节)的长度       
LINK45 = 6.5    # JOINT4与JOINT5(腕关节)的长度 
TOOL_LEN = 5.5  # 工具的长度(气泵连杆的长度)

##########################################
## 机械臂-关节设置
##
##########################################
# 关节的编号, 也是关节对应的串口总线舵机的ID号
# 注: JNT是Joint的缩写
JOINT1 = 0
JOINT2 = 1
JOINT3 = 2
JOINT4 = 3

# 关节弧度的范围
# THETA_LOWERB = [-math.pi/2, -math.pi, -math.pi/4, -math.pi/2]
THETA_LOWERB = [-math.radians(135), -math.pi, -math.pi/4, -math.pi/2]
# THETA_UPPERB = [math.pi/2, 0, 3*math.pi/4, math.pi/2]
THETA_UPPERB = [math.radians(135), 0, 3*math.pi/4, math.pi/2]

# 机械臂初始化位姿的弧度
THETA_INIT_POSE = {
    JOINT1:0, 
    JOINT2:-3*math.pi/4,
    JOINT3:math.pi/2,
    JOINT4:math.pi/4}

# 舵机原始角度与关节弧度转换对应的偏移量与比例系数
# JOINT2SERVO_K=[-56.818, 56.659, -59.842, -58.251]
JOINT2SERVO_K=[-58.855, 56.443, -57.967, -57.095]
# JOINT2SERVO_B=[-9.250,93.000,48.000,-1.600]
JOINT2SERVO_B=[-1.800, 89.795, 45.885, -1.745]
##########################################
## 轨迹规划
##
##########################################
TRAJECTORY_DELTA_T = 0.001 # 单位s


##########################################
## 插补算法
##
##########################################
RAD_PER_STEP = 0.05

#############################
## 相机参数
##
#############################
# 摄像头的设备号
# 默认为 /dev/video0
# CAM_PORT_NAME = '/dev/video0' # '/dev/video1'
CAM_PORT_NAME = '/dev/video1'

# 画面宽度
CAM_IMG_WIDTH = 2592
# 画面高度
CAM_IMG_HEIGHT = 1944
# 自动曝光
# 采集标定图片的时候/ArucoTag识别，　设置自动曝光为True
# 色块识别的时候，　设置自动曝光为False
# CAM_EXPOSURE_AUTO = True 
CAM_EXPOSURE_AUTO = False
# 相机曝光
CAM_EXPOSURE_ABSOLUTE = 391 # 239 #296 # 白天 
# CAM_EXPOSURE_ABSOLUTE = 687 # 晚上
# 相机帧率
CAM_FPS = 30
# 摄像头缓冲区的大小
CAM_BUFFERSIZE = 2 # 3
# 亮度
CAM_BRIGHNESS = 0
# 对比度
CAM_CONTRUST = 44
# 色调
CAM_HUE = 0
# 饱和度
CAM_SATURATION = 64
# 锐度
CAM_SHARPNESS = 0
# GAMMA
CAM_GAMMA = 100
# 开启自动白平衡
CAM_AWB = False
# 白平衡的温度
CAM_WHITE_BALANCE_TEMPRATURE = 6500 # 4600


#############################
## 相机标定
## 
#############################
CALI_BOARD_GRID_SIZE = 2.05 # 单位cm


#############################
## 工作台配置
##
#############################
# 工作台原点坐标在机械臂基坐标系下的位置 (单位 cm)
WORKSPACE_ORIGIN_POSI = (14., -0.5, -2.5) # (16, 0, -4)

#############################
## 色块抓取的配置参数
##
#############################
CUBIC_SIZE = 3.0 # 立方体的边长 单位cm
# 黑色背景的颜色阈值(BGR)
BLACK_BACKGROUND_LOWERB = (0, 0, 0)
BLACK_BACKGROUND_UPPERB = (50, 50, 50)

# 红色色块的颜色阈值(BGR)
RED_BLOCK_LOWERB = [(0, 0, 120), (90, 60, 150), (0, 0, 150), (0, 0, 50),(0, 0, 90)]
RED_BLOCK_UPPERB = [(90, 90, 180),(255, 255, 255), (120, 120, 255), (40, 40, 100), (70, 70, 156)] # (42, 42, 140)

# 黄色色块的颜色阈值(BGR)
YELLOW_BLOCK_LOWERB = [(23, 150, 150), (0, 90, 90)]
YELLOW_BLOCK_UPPERB = [(109, 210, 210), (125, 255, 255)]

# 蓝色色块的颜色阈值(BGR)
BLUE_BLOCK_LOWERB = [(152, 95, 0), (180, 140, 0), (180, 180, 55), (125, 75, 0)]
BLUE_BLOCK_UPPERB = [(238, 164, 44), (255, 255, 60), (255, 255, 200), (190, 150, 72)]

# 画面中色块连通域的矩形区域的尺寸
COLOR_CUBIC_CONTOUR_MIN_WIDTH = 100
COLOR_CUBIC_CONTOUR_MIN_HEIGHT = 100
COLOR_CUBIC_CONTOUR_MAX_WIDTH = 400
COLOR_CUBIC_CONTOUR_MAX_HEIGHT = 400

# 颜色的名称
COLOR_NAMES = ['RED', 'YELLOW', 'BLUE']
# 可视化所需的颜色
BGR_CANVAS_COLOR = {
    'RED': (0, 0, 255),
    'YELLOW': (0, 255, 255),
    'BLUE': (255, 0, 0)}

# 物块的BGR阈值的合集
BGR_THRESHOLDS = {
    'RED': (RED_BLOCK_LOWERB, RED_BLOCK_UPPERB),
    'YELLOW': (YELLOW_BLOCK_LOWERB, YELLOW_BLOCK_UPPERB),
    'BLUE': (BLUE_BLOCK_LOWERB, BLUE_BLOCK_UPPERB)}

# 物块位置显示坐标
BGR_CANVAS_TAG_POSI = {
    'RED': (50, 100),
    'YELLOW': (50, 200),
    'BLUE': (50, 300)}

# 四边形拟合质量的阈值条件
RECT_FIT_QUALITY_RATIO = 0.06

# 色块抓取存放位置(在机械臂基坐标系下)
COLOR_CUBIC_TARGET_POSI = {
    'RED': (1, 12, 0), # 红色色块
    'YELLOW': (1, -12, 0), # 黄色色块
    'BLUE': (10, 15, 0)} # 蓝色色块

#############################
## ArucoTag的配置参数
##
#############################
ARUCO_SIZE = 2.5 # ArucoTag的尺寸 单位cm, 打印在A4纸上面
ARUCO_IDS = [1, 2, 3] # 待识别的ArucoTag ID
# 物块位置显示坐标
ARUCO_CANVAS_TAG_POSI = {
    1: (50, 100),
    2: (50, 200),
    3: (50, 300)}

# ArucoTag物块抓取存放位置(在机械臂基坐标系下)
ARUCO_CUBIC_TARGET_POSI = {
    1: (1, -12, 0),
    2: (1, 12, 0),
    3: (10, 15, 0)}