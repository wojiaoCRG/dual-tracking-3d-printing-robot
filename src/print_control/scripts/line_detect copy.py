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
    lower_yellow = np.array([10, 25, 245])  # 喷头的HSV下限
    upper_yellow = np.array([50, 80, 255])  # 喷头的HSV上限
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)         
    
    # 寻找轮廓
    #请注意，cv2.findContours函数返回三个值：轮廓、它们的层次结构和一个返回值。在代码中，我使用_来忽略层次结构和返回值，只保留轮廓
    contours ,_= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 遍历轮廓，绘制绿色线条的边框
    for contour in contours: 
        cv2.drawContours(image_np, [contour], 0, (0, 255, 0), 2)



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


