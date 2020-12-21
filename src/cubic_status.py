''''
物块的状态信息
--------------------------------------------------
- 作者: 阿凯
- Email: xingshunkai@qq.com
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import math

class CubicStatus:
    '''物块的状态信息'''
    STABLE_CNT = 5 # 物块是否稳定的计数标准
    MAX_DIS = 2 # 距离上一帧最大的距离
    def __init__(self):
        '''初始化物块信息'''
        self.reset()

    def reset(self):
        '''重置物块的状态信息'''
        self.cnt = 0 # 更新帧数
        self.x = 0 # 物块在工作台坐标系下的x坐标
        self.y = 0 # 物块在工作台坐标系下的y坐标
        self.O = (0, 0) # 更新最近一次的色块的像素坐标

    def update(self, has_cubic:bool, new_posi:tuple, O:tuple=None):
        '''更新Cublic的状态'''
        if not has_cubic or not self.match_last_status(new_posi):
            # 物块丢失/物块移动
            self.reset() # 清空
        # 物块丢失
        if not has_cubic:
            return

        # 物块静止
        if self.cnt == 0:
            self.x, self.y = new_posi
        else:
            # 低通滤波
            nx, ny = new_posi
            self.x = self.x*0.6 + nx*0.4
            self.y = self.y*0.6 + ny*0.4
        # 四舍五入 精确到0.1cm
        self.x = round(self.x, 1)
        self.y = round(self.y, 1)
        self.cnt += 1
        # 更新最近一次的色块的像素坐标
        if O is not None:
            self.O = O
    
    def match_last_status(self, new_posi):
        '''判断当前帧跟上一帧是否匹配'''
        nx, ny = new_posi
        distance = math.sqrt((nx-self.x)**2 + (ny-self.y)**2)
        return distance <= self.MAX_DIS
    
    def has_cubic(self):
        '''画面中是否有这个立方体'''
        return self.cnt > 0

    def is_stable(self):
        '''物块是否稳定'''
        return self.cnt >= self.STABLE_CNT
