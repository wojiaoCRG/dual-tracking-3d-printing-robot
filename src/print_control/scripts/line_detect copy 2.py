# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import CompressedImage
import cv2,cv_bridge
import numpy as np



def image_callback(msg):
    # 将图像数据转换为NumPy数组
    # frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)

    # 获取图像
    #image = cv_bridge.CvBridge().imgmsg_to_cv2(msg, desired_encoding='bgr8')
    
    # 使用cv_bridge的compressed_imgmsg_to_cv2方法将CompressedImage消息转换为OpenCV图像
    np_arr = np.frombuffer(msg.data, np.uint8)
    image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    # 检测喷头位置
    # HSV (Hue, Saturation, Value) 颜色空间中检测喷头位置
    hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([10, 25, 246])  # 喷头的HSV下限
    upper_yellow = np.array([50, 80, 255])  # 喷头的HSV上限
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)         
    
    # 寻找轮廓
    #请注意，cv2.findContours函数返回三个值：轮廓、它们的层次结构和一个返回值。在代码中，我使用_来忽略层次结构和返回值，只保留轮廓
    contours ,_= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 遍历轮廓，绘制绿色线条的边框
    for contour in contours:
       if len(contour) > 150:
            # 将轮廓点转换为(x, y)的坐标形式
            points = contour.squeeze()
            # 获取y坐标最大的点，即最高点
            min_y = np.argmin(points[:, 1])
            min_point = points[min_y]
            # 以最低点为圆心，画一个半径为5×5像素的圆
            radius = 5  # 半径
            color = (255, 0, 0)  # 蓝色
            thickness = -1  # 填充圆
            cv2.circle(image_np, (min_point[0], min_point[1]), radius, color, thickness)
            cv2.drawContours(image_np, [contour], 0, (0, 255, 0), 2)

            # 获取最低点的y坐标
            y = int(min_point[1])
            # 在最低点的同一行进行扫描，寻找红色像素
            for x in range(max(0, y - 5), min(image_np.shape[1], y + 5)):
                # 检查BGR值，确定是否为红色
                if (image_np[x, y] >= [100, 0, 0]).all() and (image_np[x, y] <= [255, 100, 100]).all():
                    # 在红色像素的位置画圆
                    cv2.circle(image_np, (x, y), 5, (0, 0, 255), -1)  # 红色填充圆



    # 显示图像
    cv2.imshow('Image View', image_np)
    cv2.waitKey(1)

if __name__ == '__main__':
    # 初始化ROS节点
    rospy.init_node('image_view')

    # 订阅摄像头数据
    rospy.Subscriber('usb_cam/image_raw/compressed', CompressedImage, image_callback)


    # 等待回调函数
    rospy.spin()


