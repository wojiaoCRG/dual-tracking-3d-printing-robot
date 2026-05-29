#! /usr/bin/python3.8
# coding=utf-8

from pymycobot.mycobot import MyCobot
from pymycobot.genre import Coord
from pymycobot.genre import Angle
import time,rospy

mc = MyCobot('/dev/ttyACM0',115200)

def cobot_move():

    res = mc.get_coords()
    time.sleep(0.012)
    while not rospy.is_shutdown():

        #z轴上升0.4mm
        speed = 1
        model = 1
        move_flag = 1

        record_coords = res
        print(record_coords) 

        # 机械臂代码
        speed = 1
        model = 1
        #record_coords = [res.x, res.y, res.z, res.rx, res.ry, res.rz ]
        record_coords = res
        print(record_coords) 
        #测试效果可行，大概就是0.5mm的实际移动。

        #测试机械臂能够正常动作的最小位移与频率，在世界坐标系下小位移高频率运动，
        if move_flag:
            record_coords[0] += 1
            mc.send_coords(record_coords,speed,model)
            move_flag = 1
            print("右超限，左回归中")
            time.sleep(0.1) 

        elif record_coords[0] > 194:
            record_coords[0] -= 1
            mc.send_coords(record_coords,speed,model)
            move_flag = 0
            print("左超限，右回归中")
            time.sleep(0.1)  


def go_home():
        mc.send_coords([195, -37.3, -67, -177.85, -1.3, 136.44], 1, 1)
        time.sleep(3)  # 等待100ms


if __name__ == '__main__':
    #回到设置打印姿态
    go_home()
    try:
        # 初始化ROS节点
        rospy.init_node('cobot_move_node')
        cobot_move()

    except rospy.ROSInterruptException:
        pass