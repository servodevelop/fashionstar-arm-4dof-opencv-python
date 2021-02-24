'''
气泵模块
--------------------------------------------------
- 作者: 阿凯
- Email: kyle.xing@fashionstar.com.hk
- 更新时间: 2020-03-11
--------------------------------------------------
'''
import time
import logging
from config import GPIO_MAGNETIC_SWITCH,GPIO_PUMP_MOTOR,MICRO_PUMP_SWITCH

if MICRO_PUMP_SWITCH:
    from gpiozero import LED as PumpMotor
    from gpiozero import LED as MagneticSwitch

class MicroPump:
    def __init__(self):
        if MICRO_PUMP_SWITCH:
            logging.info("[micro pump]初始化气泵电机与电磁阀的GPIO资源")
            self.motor = PumpMotor(GPIO_PUMP_MOTOR)
            self.switch = PumpMotor(GPIO_MAGNETIC_SWITCH)
            self.motor.off()
            self.switch.off()
        else:
            logging.info("[micro pump]一个假的气泵初始化")

    def on(self, delay=True):
        '''气泵吸气'''
        if MICRO_PUMP_SWITCH:
            # 气泵开
            self.motor.on()
            logging.info("[micro pump]打开气泵")
        if delay:
            # 等待一段时间
            time.sleep(1.0)

    def off(self):
        '''气泵放气'''
        if MICRO_PUMP_SWITCH:
            logging.info('[micro pump] 关闭气泵的电机')
            # 气泵关
            self.motor.off()

        time.sleep(0.3)
        # 放气过程 : 放气->延时->关闭->延时 (循环三次)
        for rpt_i in range(1):
            if MICRO_PUMP_SWITCH:
                logging.info('[micro pump] 电磁阀开')
                self.switch.on()
            time.sleep(0.3)
            if MICRO_PUMP_SWITCH:
                logging.info('[micro pump] 电磁阀关')
                self.switch.off()
            time.sleep(0.3)
        time.sleep(0.5)
