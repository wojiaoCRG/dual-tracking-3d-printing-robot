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

# mc.set_pin_mode(3,2)
# mc.set_pin_mode(1,2)
# mc.set_pin_mode(16,2)
# mc.set_pin_mode(17,2)
# mc.set_pin_mode(2,2)
# mc.set_pin_mode(5,2)
# mc.set_pin_mode(35,2)
# mc.set_pin_mode(26,2)

def car_run():
    # 初始化 Twist 控制消息
    twist = Twist()
    twist.linear.x = 0.02
    twist.angular.z = 0
    #设置频率
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        try:
            # 尝试获取传感器输入
            sensor1 = mc.get_basic_input(18)
            time.sleep(0.1)
            sensor2 = mc.get_basic_input(19)
            time.sleep(0.1)
            sensor3 = mc.get_basic_input(16)
            time.sleep(0.1)
            sensor4 = mc.get_basic_input(17)
            time.sleep(0.1)
            sensor5 = mc.get_basic_input(2)
            time.sleep(0.1)
            sensor6 = mc.get_basic_input(5)
            time.sleep(0.1)
            sensor7 = mc.get_basic_input(35)
            time.sleep(0.1)
            sensor8 = mc.get_basic_input(26)
            print("%d %d %d %d %d %d %d %d" %(sensor1, sensor2,sensor3,sensor4,sensor5,sensor6,sensor7,sensor8))
            if not sensor1 and not sensor2 and not sensor3 and not sensor4 and not sensor5 and not sensor6 and not sensor7 and not sensor8:
                twist.angular.z = 0
            elif sensor1 or sensor2 or sensor3 or sensor4:
                twist.angular.z = 0.2
            elif sensor5 or sensor6 or sensor7 or sensor8:
                twist.angular.z = -0.2
        except Exception as e:
            # 如果获取传感器输入失败，打印错误信息
            rospy.logerr("Error getting sensor input: %s", e)

        # 发布控制命令
        cmd_vel.publish(twist)
        rate.sleep()

if __name__ == '__main__':
    car_run()