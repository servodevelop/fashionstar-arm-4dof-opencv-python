'''
OpenCV常用函数-工具箱
--------------------------------------------------
- 作者: 阿凯
- Email: kyle.xing@fashionstar.com.hk
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import cv2
import numpy as np

def find_contours(img_bin:np.array):
    '''寻找连通域(OpenCV版本兼容)'''
    contours = None
    if cv2.__version__[0] == '4':
        contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        img, contours, hierarchy =  cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def find_max_contour(img_bin:np.array, min_width:int, min_height:int, max_width:int, max_height:int, offset:tuple=(0, 0)):
    '''寻找最大的连通域'''
    
    # 寻找连通域
    contours = find_contours(img_bin)
    # 寻找面积最大的连通域
    candi_rects = [(cnt, cv2.boundingRect(cnt)) for cnt in contours]
    # 根据面积进行筛选(添加过滤器)
    candi_rects = list(filter(lambda rect: rect[1][2]>=min_width and rect[1][3] >=min_height and \
        rect[1][2]<=max_width and rect[1][3]<=max_height, candi_rects))
    if len(candi_rects) == 0:
        # 连通域分割后,没有合适的Rect区域
        return False, None
    # 获取最大的countor
    contour, local_rect = max(candi_rects, key=lambda rect: rect[1][2] * rect[1][3])
    # ROI区域添加偏移量
    x0, y0 = offset
    x1,y1, w, h = local_rect
    global_rect = (x1+offset[0], y1+offset[1], w, h) # 全局图像的矩形区域
    # 计算全局下的contour坐标
    n_point = len(contour)
    contour = contour.reshape((n_point, 2))
    contour[:,0] += x0
    contour[:,1] += y0
    contour = contour.reshape((n_point, 1, 2))
    # 返回找到的最大连通域的矩形
    return True, (global_rect, contour)

