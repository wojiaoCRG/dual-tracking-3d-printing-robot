#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
from pymycobot.mycobot import MyCobot

# 初始化 MyCobot 对象
mc = MyCobot('/dev/ttyACM0', 115200)

# 初始化ROS节点
rospy.init_node('car_run')

# 初始化控制命令发布者
cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=1)

def car_run():
    # 初始化 Twist 控制消息
    twist = Twist()
    twist.linear.x = 0.015
    twist.angular.z = 0
    #设置频率
    rate = rospy.Rate(10)
    #设置引脚模式
    mc.set_pin_mode(23, 0)
    mc.set_pin_mode(33, 0)
    mc.set_pin_mode(35, 0)
    mc.set_pin_mode(36, 0)
    #定义当前状态位
    state = 'forward'
    while not rospy.is_shutdown():
        try:
            # 尝试获取传感器输入
            sensor3 = mc.get_digital_input(33)
            sensor4 = mc.get_basic_input(36)
            sensor5 = mc.get_basic_input(35)
            sensor6 = mc.get_digital_input(23)
            print("%d,%d,%d,%d" % (sensor3,sensor4, sensor5,sensor6))
            Vz= twist.angular.z
            if not sensor3 and ((not sensor4 and not sensor5) or (sensor4 and sensor5)) and not sensor6 and (state == 'forward' or state == 'turn_left_4' or state == 'turn_right'):
                if Vz >-0.01 and Vz < 0.01:  
                    Vz = 0
                    state = 'forward'
                elif Vz > 0:
                    Vz -= 0.01
                elif Vz < 0:
                    Vz += 0.01
            elif not sensor3 and not sensor4 and not sensor5 and not sensor6 and state == 'turn_left_1':
                Vz += 0.01
            elif sensor3:
                Vz += 0.01
                state = 'turn_left_1'
            elif sensor4:
                Vz += 0.01
                state = 'turn_left_4'
            elif sensor5 or sensor6:
                Vz -= 0.01
                state = 'turn_right'

            if Vz >= 0.1:
                Vz = 0.2
            elif Vz <= -0.1:
                Vz = -0.2
        except Exception as e:
            # 如果获取传感器输入失败，打印错误信息
            rospy.logerr("Error getting sensor input: %s", e)
        # 发布控制命令
        print(twist.angular.z)
        twist.angular.z = Vz
        cmd_vel.publish(twist)
        rate.sleep()

if __name__ == '__main__':
    car_run()