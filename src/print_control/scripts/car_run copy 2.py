#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
from pymycobot.mycobot import MyCobot
import time


# 初始化 MyCobot 对象
mc = MyCobot('/dev/ttyACM0', 115200)

# 初始化ROS节点
rospy.init_node('car_run')

# 初始化控制命令发布者
cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=1)

# Define GPIO pins
CLK = 33
DAT = 23

#设置引脚模式
mc.set_pin_mode(CLK,1)
mc.set_pin_mode(DAT,2)

#定义存储数组 
a = [0 for j in range(8)]

def gw_gray_serial_read_simple():
    ret = 0
    # Read 8 bits from the sensor
    for i in range(8):
        mc.set_digital_output(CLK ,0)  # Clock falling edge
        ret |= ((mc.get_digital_input(DAT)) << i)
        mc.set_digital_output(CLK ,1)  # Clock rising edge
        time.sleep(0.000005)  # Delay of 5 microseconds
    return ret


def loop():
    while not rospy.is_shutdown():
        # Read sensor data
        sensor_status = gw_gray_serial_read_simple() 
        for i in range(8):
            # 获取第N位bit
            print((sensor_status >> i) & 0x1, end=' ')
        print()
        
        time.sleep(0.5)  # 500 ms delay

try:
    loop()
except KeyboardInterrupt:
    pass
