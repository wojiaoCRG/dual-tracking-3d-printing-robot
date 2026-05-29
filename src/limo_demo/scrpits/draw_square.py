#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
import math

INTRODUCTION = """
---------------------------
发布控制命令使小车以正方形轨迹运动
---------------------------
"""
# 打印功能信息
print(INTRODUCTION)


# 初始化 ros 节点
rospy.init_node("draw_square", anonymous=True)

# 初始化控制命令发布者
cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)

# 初始化 Twist 控制消息
twist = Twist()
twist.linear.x = 0.1  # 线速度为0.1m/s


# 初始化 ros主循环
rate = rospy.Rate(2)
count=0
PI=math.pi

while not rospy.is_shutdown():
    twist.angular.z = 0    # 初始角速度为0，即不进行旋转
    count+=1
    while(count==10):
        count=0
        twist.angular.z=PI    #转90度,因为一次循环0.5s，所以转PI的一半
    cmd_vel_pub.publish(twist)
    rate.sleep()  # 控制频率为2Hz，因此睡眠0.5s以保持频率稳定
    
