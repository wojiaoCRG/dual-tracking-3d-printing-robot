#! /usr/bin/python3.8
# coding=utf-8

from pymycobot.mycobot import MyCobot
from geometry_msgs.msg import Twist
import time,rospy
import cv2
import numpy as np

mc = MyCobot('/dev/ttyACM0',115200)

cap = cv2.VideoCapture(1)

# 初始化控制命令发布者
cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=1)


def run_print():
    
    
    #mc.set_basic_output(5,1)    #方向位
    #mc.set_basic_output(26,0)   #使能位，0为使能
    #mc
    time.sleep(0.012)
    res = mc.get_coords()   #在循环里读取机械臂坐标会导致机械臂下坠！！！
    time.sleep(0.02)

    # 初始化 Twist 控制消息
    twist = Twist()
    twist.linear.x = 0.01
    twist.angular.z = 0
    #设置频率
    #rate = rospy.Rate(10)
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

            if Vz >= 0.2:
                Vz = 0.2
            elif Vz <= -0.2:
                Vz = -0.2
        except Exception as e:
            # 如果获取传感器输入失败，打印错误信息
            rospy.logerr("Error getting sensor input: %s", e)
        # 发布控制命令
        print(twist.angular.z)
        twist.angular.z = Vz
        cmd_vel.publish(twist)

        #-----------------------------------------------------------------
        # 挤出机代码
        #count = 100
       # while count > 0:
            #count -= 1
        #mc.set_basic_output(2,1)
        #time.sleep(0.004134)
        #mc.set_basic_output(2,0)
       # time.sleep(0.004134)
        #print("extruder_thread_function")
        
        #-------------------------------------------------------
        # 读取一帧视频
        ret, frame = cap.read()
        if not ret:
            break
        # 保存图像
        #cv2.imwrite( 'src/print_control/scripts/image3.jpg',image_np)
        
        # 定义正方形区域的坐标
        x1, y1 = 100,85  # 左上角
        x2, y2 = 464 ,90 # 右下角
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # BGR颜色空间中，(0, 255, 0)代表绿色
        # 创建一个与原图像大小相同的边缘图像
        zeromask = np.zeros_like(frame)
        zeromask[y1:y2,x1:x2] = 1
        roi = frame * zeromask

        #roi = image_np_copy[y1:y2, x1:x2]

        # 检测喷头位置
        # HSV (Hue, Saturation, Value) 颜色空间中检测喷头位置
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([0,10, 50])  # 喷头的HSV下限
        #upper_yellow = np.array([50, 70, 210])  # 喷头的HSV上限
        upper_yellow = np.array([59, 255, 255])  # 喷头的HSV上限
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)     
        # 寻找轮廓
        #请注意，cv2.findContours函数返回三个值：轮廓、它们的层次结构和一个返回值。在代码中，我使用_来忽略层次结构和返回值，只保留轮廓
        contours ,_= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 初始化 x 坐标的最值
        min_x = float('inf')
        max_x = float('-inf')

        # 初始化最大轮廓和最大面积
        max_contour = None
        max_area = 0

        # 遍历所有轮廓
        for contour in contours:
            # 计算轮廓面积
            area = cv2.contourArea(contour)

            # 找到最大轮廓
            if area > max_area:
                max_area = area
                max_contour = contour

        # 画出最大轮廓
        if max_contour is not None:
            # 遍历轮廓中的每个点
            for point in max_contour:
                x, y = point[0]
                # 更新 x 坐标的最值
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x 
            cv2.drawContours(frame, [max_contour], 0, (255, 0, 0), 3)
        # 计算 x 坐标的最值的平均值
        if min_x != float('inf') and max_x != float('-inf'):
            average_x = (min_x + max_x) / 2
            print(f"轮廓的 x 坐标最值的平均值为：{average_x}")
        else:
            average_x = 278
            print("没有找到有效的轮廓")



        # 机械臂代码
        speed = 1
        model = 1
        coords = res
        print(coords)

        if (average_x is not None) and ((abs(average_x - 292))> 10):  #减数292为喷头在图像中的像素位，手眼标定

            print("喷头位置不正确")
    
            #测试效果可行，大概就是0.5mm的实际移动。

            #测试机械臂能够正常动作的最小位移与频率，在世界坐标系下小位移高频率运动，
            if average_x > 292 :
                if coords is not None and coords[0] > 174:
                    coords[0] -= 0.2  #数值过大会导致振荡，反复调节才能到指定位置
                    mc.send_coords(coords,speed,model)   #这两句导致机械臂没有命令时下坠
                    time.sleep(0.1)  
                    print("右调")
                else:
                    print("超出右限位")
            else:
                if coords is not None and coords[0] < 214:
                    coords[0] += 0.2
                    mc.send_coords(coords,speed,model)  #这两句导致机械臂没有命令时下坠。
                    time.sleep(0.1) 
                    print("左调")
                else:
                    print("超出左限位")


        else:
            print("喷头位置正确")


        # 显示图像
        flipped_image = cv2.flip(frame, -1)
        cv2.imshow('Image View', flipped_image)
        cv2.waitKey(1)



def go_home():
        mc.send_coords([187, -60, -70, 180, 0, -45], 1, 1)  
        time.sleep(5)  # 等待100ms


if __name__ == '__main__':
    #回到设置打印姿态
    go_home()
    try:
        # 初始化ROS节点
        rospy.init_node('run_print')
        run_print()

    except rospy.ROSInterruptException:
        pass