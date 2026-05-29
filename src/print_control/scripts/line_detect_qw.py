# -*- coding: utf-8 -*-
import rospy
from sensor_msgs.msg import CompressedImage
import cv2,cv_bridge
import numpy as np

def image_callback(msg):

    # 将CompressedImage消息转换为OpenCV图像
    np_arr = np.frombuffer(msg.data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # 转换到HSV空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 设置红色HSV范围
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])

    # 创建掩码
    mask = cv2.inRange(hsv, lower_red, upper_red)

    # 应用形态学操作去除噪点
    kernel = np.ones((6, 6),np.uint8)
    mask_close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 寻找轮廓
    contours, _ = cv2.findContours(mask_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 绘制丝材的中心线

    for cnt in contours:
        if len(cnt) > 100:
            # 获取最小外接矩形
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            # 计算中心线 center 是旋转矩形的中心点坐标。angle 是旋转矩形的旋转角度，以度为单位。width 和 height 分别是旋转矩形的宽度和高度。
            #旋转矩形的旋转角度通常是指矩形的长边与水平轴之间的夹角
            center, (width, height), angle = rect #x轴方向边为width
            if width < height:
                angle += 90   
            
            start_point  = (int(center[0] - np.cos(angle) * height/2) , int(center[1] + np.sin(angle) * height/2))
            end_point = (int(center[0] + np.cos(angle) * height/2), int(center[1] - np.sin(angle) * height/2))          
            # #根据三角函数确定中心线的起点终点
            start_point  = (int(center[0] - np.cos(angle) * height/2), int(center[1] + np.sin(angle) * height/2))
            end_point = (int(center[0] + np.cos(angle) * height/2), int(center[1] - np.sin(angle) * height/2)) 

            # M = cv2.getRotationMatrix2D(center, angle, 1)
            # center_line = np.dot(M[:2,:2], np.float32([[0,height/2], [width, height/2]]) +center) 

            # 绘制轮廓和中心线
            # cv2.drawContours(image, [box], 0, (0, 0, 255), 2)
            # cv2.line(image, start_point, end_point, (0, 255, 0), 2)

    # 显示图像
    cv2.imshow('Image View', image)
    # cv2.imshow('mask_close', mask_close)
    cv2.waitKey(1)

if __name__ == '__main__':
    rospy.init_node('image_view')
    rospy.Subscriber('usb_cam/image_raw/compressed', CompressedImage, image_callback)
    rospy.spin() 