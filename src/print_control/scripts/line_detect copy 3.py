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

    # 保存图像
    #cv2.imwrite( 'src/print_control/scripts/image1.jpg',image_np)


    # 检测喷头位置
    # HSV (Hue, Saturation, Value) 颜色空间中检测喷头位置
    hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([0, 110, 40])  # 喷头的HSV下限
    upper_yellow = np.array([10, 250, 112])  # 喷头的HSV上限
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow) 

    # 创建一个新的全黑的掩码，与原图大小相同
    square_mask = np.zeros_like(mask) 

    # 定义正方形区域的坐标
    x1, y1 = 250, 230  # 左上角
    x2, y2 = 300, 260  # 右下角
    cv2.rectangle(image_np, (x1, y1), (x2, y2), (0, 255, 0), 2)  # BGR颜色空间中，(0, 255, 0)代表绿色

    # 在新掩码上绘制一个白色的正方形
    square_mask[y1:y2,x1:x2] = 1

    final_mask = cv2.bitwise_and(mask, square_mask)
    

    # 寻找轮廓
    #请注意，cv2.findContours函数返回三个值：轮廓、它们的层次结构和一个返回值。在代码中，我使用_来忽略层次结构和返回值，只保留轮廓
    contours ,_= cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 遍历轮廓，绘制绿色线条的边框
    for contour in contours:
       if  len(contour) > 5  :
            # 将轮廓点转换为(x, y)的坐标形式
            points = contour.squeeze()
            # 获取y坐标最小的点，即最高点
            min_y = np.argmin(points[:, 1])
            min_point = points[min_y]
            # 以最低点为圆心，画一个半径为5×5像素的圆
            radius = 5  # 半径
            color = (255, 0, 0)  # 蓝色
            thickness = -1  # 填充圆
            cv2.circle(image_np, (min_point[0], min_point[1]), radius, color, thickness)
            cv2.drawContours(image_np, [contour], 0, (0, 255, 0), 2)

            # 获取最低点的y坐标
            y_min = int(min_point[1])
            # 在最低点的同一行进行扫描，寻找红色像素
            #for y in range(max(0, y_min - 20), min(image_np.shape[1], y_min )):
            for y in range(max(0, 230), min(image_np.shape[1], 240)):
    
                for x in range(0, image_np.shape[0]):
                    if (image_np[x, y] >= [0, 0, 140]).all() and (image_np[x, y] <= [40, 80, 240]).all():
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


