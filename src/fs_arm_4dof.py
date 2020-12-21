'''
Fashion Star 4自由度机械臂Python SDK
--------------------------------------------------
- 作者: 阿凯
- Email: xingshunkai@qq.com
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import time # 时间
import logging # 日志管理
import serial # 串口通信
from fs_uservo import UartServoManager # 导入串口舵机管理器
from minimum_jerk import minimum_jerk_plan, minimum_jerk_seq # 轨迹规划算法
from config import * # 导入配置文件
import numpy as np

# 设置日志等级
# logging.basicConfig(level=logging.INFO)

class Arm4DoF:
    def __init__(self, device:str=DEVICE_PORT_DEFAULT, is_init_pose:bool=True):
        '''机械臂初始化'''
        # 创建串口对象
        try:
            self.uart = serial.Serial(port=device, baudrate=115200,\
                     parity=serial.PARITY_NONE, stopbits=1,\
                     bytesize=8,timeout=0)
            # 创建串口舵机管理器
            self.uservo = UartServoManager(self.uart, srv_num=SERVO_NUM)
            # InitPose
            if is_init_pose:
                self.init_pose()
        except serial.SerialException as e:
            logging.error('该设备不存在,请重新填写UART舵机转接板的端口号')

    def init_pose(self):
        '''机械臂位姿初始化'''
        self.set_joint(THETA_INIT_POSE, wait=True)
    
    def set_servo_velocity(self, speed:float):
        '''设置舵机的转速 单位°/s'''
        self.uservo.mean_dps = max(min(abs(speed), SERVO_SPEED_MAX), SERVO_SPEED_MIN)

    def set_servo_angle(self, angles, wait:bool=False):
        '''设置舵机的原始角度'''
        if type(angles) == list:
            for srv_idx, angle in enumerate(angles):
                logging.info('设置舵机角度, 舵机#{} 目标角度 {:.1f}'.format(srv_idx, angle))
                self.uservo.request_set_srv_angle(int(srv_idx), float(angle))
        elif type(angles) == dict:
            for srv_idx, angle in angles.items():
                logging.info('设置舵机角度, 舵机#{} 目标角度 {:.1f}'.format(srv_idx, angle))
                self.uservo.request_set_srv_angle(int(srv_idx), float(angle))
        if wait:
            self.wait() # 等待舵机角度到达目标角度
    
    def set_joint(self, thetas, wait:bool=False, interval=None):
        '''设置关节的弧度'''
        if type(thetas) == list:
            for srv_idx, theta in enumerate(thetas):
                # 检查弧度的范围约束
                theta = min(max(THETA_LOWERB[srv_idx], theta), THETA_UPPERB[srv_idx])
                logging.info('设置关节弧度, 关节#{}  弧度 {:.4f} 角度 {:.1f}'.format(srv_idx+1, theta, math.degrees(theta)))
                # 根据关节的弧度计算出舵机的原始角度
                angle = JOINT2SERVO_K[srv_idx]*theta + JOINT2SERVO_B[srv_idx] 
                self.uservo.request_set_srv_angle(int(srv_idx), float(angle), interval=interval)
        elif type(thetas) == dict:
            for srv_idx, theta in thetas.items():
                 # 检查弧度的范围约束
                theta = min(max(THETA_LOWERB[srv_idx], theta), THETA_UPPERB[srv_idx])
                logging.info('设置关节弧度, 关节#{} 弧度 {:.4f} 角度 {:.1f}'.format(srv_idx+1, theta, math.degrees(theta)))
                # 根据关节的弧度计算出舵机的原始角度
                angle = JOINT2SERVO_K[srv_idx]*theta + JOINT2SERVO_B[srv_idx] 
                self.uservo.request_set_srv_angle(int(srv_idx), float(angle), interval=interval)
        if wait:
            self.wait() # 等待舵机角度到达目标角度
    
    def trajectory_plan(self, joint_id:int, theta_e:float, T:float, w_s:float=0.0, w_e:float=0.0, a_s:float=0, a_e:float=0):
        '''Minimum Jerk轨迹规划'''
        # 获取当前关节的
        theta_s = self.get_thetas()[joint_id]
        c = minimum_jerk_plan(theta_s, theta_e, w_s, w_e, a_s, a_e, T)
        t_arr, theta_arr = minimum_jerk_seq(T, c, delta_t=TRAJECTORY_DELTA_T)
        return t_arr, theta_arr
    
    def set_joint2(self, thetas, T:float):
        '''设置关节弧度2-带MinimumJerk 轨迹规划版本,需要阻塞等待.
        '''
        # 将thetas转换为dict类型
        if type(thetas) == list:
            thetas_arr = thetas
            thetas = {}
            for joint_id, theta in enumerate(thetas_arr):
                thetas[joint_id] = theta

        # theta序列
        theta_seq_dict = {}
        
        t_arr = None # 时间序列
        # 生成轨迹序列
        for joint_id, theta_e in thetas.items():
            t_arr, theta_arr = self.trajectory_plan(joint_id, theta_e, T)
            # print("joint{} theta_arr: {}".format(joint_id, theta_arr))
            # print(theta_arr)
            theta_seq_dict[joint_id] = theta_arr # np.copy(theta_arr)
        
        # 按照轨迹去执行
        i = 0
        tn = len(t_arr)
        while True:
            if i >= tn:
                break
            t_start = time.time()
            next_thetas = {}
            for joint_id in thetas.keys():
                next_thetas[joint_id] = theta_seq_dict[joint_id][i]
            # 设置关节弧度
            self.set_joint(next_thetas, interval=0)
            # print('t_i={} next_thetas: {}'.format(i, next_thetas))
            t_end = time.time()
            # print('t_end - t_start = {:.4f}'.format(t_end-t_start))
            # time.sleep(TRAJECTORY_DELTA_T-(t_end - t_start)) # 延迟
            m = int(math.floor((t_end - t_start) / TRAJECTORY_DELTA_T))
            i += (1 + m)
            # 补齐所需延迟等待的时间
            time.sleep(TRAJECTORY_DELTA_T - ((t_end - t_start) - m*TRAJECTORY_DELTA_T))
        return theta_seq_dict

    def inverse_kinematics(self, p_tool:list):
        '''逆向运动学'''
        theta1 = math.atan2(p_tool[1], p_tool[0]) # 获得关节1的弧度
        if theta1 < THETA_LOWERB[JOINT1] or theta1 > THETA_UPPERB[JOINT1]:
            logging.warning('theta1={}, 超出了关节1弧度范围'.format(theta1))
        # 计算joint5的坐标
        p_joint5 = [p_tool[0], p_tool[1], p_tool[2]+TOOL_LEN]
        # 计算joint4的坐标
        p_joint4 = [
            p_joint5[0] - LINK45*math.cos(theta1),
            p_joint5[1] - LINK45*math.sin(theta1),
            p_joint5[2]]
        #　得到了Joint4的坐标之后, 后续就是按照3DoF机械臂逆向运动学求解的方法
        x, y, z = p_joint4
        distance = math.sqrt(x**2 + y**2 + z**2)
        if distance > (LINK23 + LINK34):
            logging.warning('超出机械臂的工作范围')
            return False, None
        # 求解theta3
        b = 0
        if math.cos(theta1) != 0:
            b = x/math.cos(theta1)
        else:
            b = y/math.sin(theta1)
        # 求解theta3
        cos_theta3 = (z**2 + b**2 - LINK23**2 - LINK34**2)/(2*LINK23*LINK34)
        sin_theta3 = math.sqrt(1 - cos_theta3**2)
        theta3 = math.atan2(sin_theta3, cos_theta3)
        # if theta3 > math.pi/2: theta3 = theta3 - math.pi
        if theta3 < THETA_LOWERB[JOINT3] or theta3 > THETA_UPPERB[JOINT3]:
            logging.warning('theta3={}, 超出了关节3弧度范围'.format(theta3))
            return False, None
        # 求解theta2
        k1 = LINK23 + LINK34 * math.cos(theta3)
        k2 = LINK34 * math.sin(theta3)
        r = math.sqrt(k1**2+k2**2)
        theta2 = math.atan2(-z/r, b/r) - math.atan2(k2/r, k1/r)
        if theta2 < THETA_LOWERB[JOINT2] or theta2 > THETA_UPPERB[JOINT2]:
            logging.warning('theta2={}, 超出了关节2弧度范围'.format(theta2))
            return False, None
        # 求解theta4
        # 默认设置LINK45始终与桌面平行 0 = theta2 + theta3 + theta4
        theta4 = - (theta2 + theta3)
        if theta4 < THETA_LOWERB[JOINT4] or theta4 > THETA_UPPERB[JOINT4]:
            logging.warning('theta4={}, 超出了关节4弧度范围'.format(theta4))
            return False, None
        
        return True, [theta1, theta2, theta3, theta4]
    def get_servo_angles(self, theta_type:type = list):
        '''获取当前关节的舵机原始角度'''
        srv_angles = []
        for srv_idx in range(SERVO_NUM):
            srv_angles.append(self.uservo.srv_info_dict[srv_idx].angle)
        if theta_type == dict:
            srv_angle_dict = {}
            for srv_id, srv_angle in enumerate(srv_angles):
                srv_angle_dict[srv_id] = srv_angle
                return srv_angle_dict
        return srv_angles
        
    def get_thetas(self, theta_type:type = list):
        '''获取当前关节的弧度'''
        thetas = []
        for srv_idx in range(SERVO_NUM):
            # 角度转换为弧度
            theta = (self.uservo.srv_info_dict[srv_idx].angle - JOINT2SERVO_B[srv_idx]) / JOINT2SERVO_K[srv_idx]
            thetas.append(theta)
        if theta_type == dict:
            # 转换为list格式
            thetas_dict = {}
            for joint_id, theta in enumerate(thetas):
                thetas_dict[joint_id] = theta
            return thetas_dict
        else:
            return thetas

    def move(self, p_tool:list, wait:bool=False, is_linear:bool=True):
        '''控制机械臂的末端旋转到特定的位置'''
        ret, thetas = self.inverse_kinematics(p_tool)
        if ret:
            logging.info('移动机械臂末端到: {}'.format(p_tool))
            if is_linear:
                self.linear_interpolation(p_tool)
            else:
                self.set_joint(thetas, wait=wait)
        else:
            logging.warn('机械臂末端不能到达: {}'.format(p_tool))

    def move2(self, p_tool:list, T:float, wait:bool=False, theta4_offset:float=0.0):
        '''使用minimum jerk测试机械臂的运动'''
       
        ret, thetas = self.inverse_kinematics(p_tool)
        if not ret:
            logging.error('超出工作空间, 机械臂末端到达不了{}'.format(p_tool))
            return False
        thetas[JOINT4] += theta4_offset # 给theta4添加补偿    
        self.set_joint2(thetas, T)

    def linear_interpolation(self, p_tool:list):
        '''关节空间下的线性插补'''
        # 获取当前关节的弧度
        cur_thetas = self.get_thetas() 
        # 获取目标的弧度
        ret, next_thetas = self.inverse_kinematics(p_tool)
        if not ret:
            logging.warn('机械臂末端不能到达: {}'.format(p_tool))
            return
        
        # 计算要分成多少步
        # 计算关节空间下的欧氏距离
        dthetas = [next_thetas[j] -cur_thetas[j] for j in range(SERVO_NUM)]
        distance = math.sqrt(sum([dtheta**2 for dtheta in dthetas]))
        n_step = int(distance / RAD_PER_STEP)
        # 逐步逼近
        for i_step in range(1, n_step+1):
            mid_thetas = [cur_thetas[j]+(i_step/n_step)*dthetas[j] for j in range(SERVO_NUM)]
            # 重新计算theta4
            mid_thetas[JOINT4] = - (mid_thetas[JOINT2] + mid_thetas[JOINT3])
            self.set_joint(mid_thetas)
            self.wait()

        self.set_joint(next_thetas)
        self.wait()
    
    def wait(self):
        '''机械臂等待'''
        while not self.uservo.is_stop():
            # 等待10ms
            time.sleep(0.001)

if __name__ == "__main__":
    arm = Arm4DoF()
