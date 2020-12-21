'''
测试色块识别与测量
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

cv2.namedWindow('img_raw',flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
cv2.namedWindow('canvas',flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

# 从视频流里面获取图像并进行色块角点识别
cam = Camera(CAM_PORT_NAME)
cam.init_camera()
cam.load_cam_calib_data() # 载入图像标定数据
capture = cam.get_video_capture()

# 物块状态合计
cubic_stats = {  
    'RED': CubicStatus(),
    'YELLOW': CubicStatus(),
    'BLUE': CubicStatus()}

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
    
capture.release()
cv2.destroyAllWindows()