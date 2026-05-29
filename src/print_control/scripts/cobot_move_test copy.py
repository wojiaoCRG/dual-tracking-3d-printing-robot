#! /usr/bin/python3.8
# coding=utf-8

from pymycobot.mycobot import MyCobot
from pymycobot.genre import Coord
from pymycobot.genre import Angle
import time,rospy

mc = MyCobot('/dev/ttyACM0',115200)

def cobot_move():
    mc.set_basic_output(5,1)    #方向位
    mc.set_basic_output(26,0)   #使能位，0为使能
    #mc
    time.sleep(0.012)
    res = mc.get_coords()
    time.sleep(0.012)
    while not rospy.is_shutdown():
            # 挤出机代码
            count = 150
            while count > 0:
                count -= 1
                mc.set_basic_output(2,1)
                time.sleep(0.01653)
                mc.set_basic_output(2,0)
                time.sleep(0.01653)
                print("extruder_thread_function")
            #z轴上升0.4mm
            speed = 1
            model = 1

            record_coords = res
            print(record_coords) 
            record_coords[2] += 0.75        
            mc.send_coords(record_coords,speed,model)
            time.sleep(0.5)  


            # # 机械臂代码
            # speed = 1
            # model = 1
            # #record_coords = [res.x, res.y, res.z, res.rx, res.ry, res.rz ]
            # record_coords = res
            # print(record_coords) 
            # #测试效果可行，大概就是0.5mm的实际移动。

            # #测试机械臂能够正常动作的最小位移与频率，在世界坐标系下小位移高频率运动，

            # record_coords[0] += 1        
            # mc.send_coords(record_coords,speed,model)
            # time.sleep(0.1)  
            # record_coords[0] += 0.5         
            # mc.send_coords(record_coords,speed,model)
            # time.sleep(0.1) 
            # record_coords[0] += 0.5        
            # mc.send_coords(record_coords,speed,model)
            # time.sleep(0.1)  
            # record_coords[0] += 0.5         
            # mc.send_coords(record_coords,speed,model)
            # time.sleep(0.1)               

            # record_coords[0] -= 1
            # mc.send_coords(record_coords,speed,model)
            # time.sleep(0.1) 
            # record_coords[0] -= 0.5
            # mc.send_coords(record_coords,speed,model)
            # time.sleep(0.1) 
            # record_coords[0] -= 0.5
            # mc.send_coords(record_coords,speed,model)
            # time.sleep(0.1) 
            # record_coords[0] -= 0.5
            # mc.send_coords(record_coords,speed,model)
            # time.sleep(0.1) 
            # print("cobot_move_thread_function")



def go_home():
        mc.send_coords([190.89999389648438, -64.0999984741211, -64.30000305175781, 177.8000030517578, 5.989999771118164, 137.57000732421875], 1, 1)
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