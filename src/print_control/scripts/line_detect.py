# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import CompressedImage
import cv2,cv_bridge
import numpy as np



def image_callback(msg):
    np_arr = np.frombuffer(msg.data, np.uint8)
    image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    image_np_copy = image_np.copy()
    # # 保存图像
    # #cv2.imwrite( 'src/print_control/scripts/image3.jpg',image_np)
    
    # # 定义正方形区域的坐标
    # x1, y1 = 150,370  # 左上角
    # x2, y2 = 450 ,375 # 右下角
    # cv2.rectangle(image_np_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)  # BGR颜色空间中，(0, 255, 0)代表绿色
    # # 创建一个与原图像大小相同的边缘图像
    # zeromask = np.zeros_like(image_np)
    # zeromask[y1:y2,x1:x2] = 1
    # roi = image_np_copy * zeromask

    # #roi = image_np_copy[y1:y2, x1:x2]

    # # 检测喷头位置
    # # HSV (Hue, Saturation, Value) 颜色空间中检测喷头位置
    # hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    # lower_yellow = np.array([0, 20, 130])  # 喷头的HSV下限
    # upper_yellow = np.array([50, 70, 210])  # 喷头的HSV上限
    # mask = cv2.inRange(hsv, lower_yellow, upper_yellow)     
    # # 寻找轮廓
    # #请注意，cv2.findContours函数返回三个值：轮廓、它们的层次结构和一个返回值。在代码中，我使用_来忽略层次结构和返回值，只保留轮廓
    # contours ,_= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # # 初始化 x 坐标的最值
    # min_x = float('inf')
    # max_x = float('-inf')

    # # 遍历每个轮廓
    # for contour in contours:
    #     # 遍历轮廓中的每个点
    #     for point in contour:
    #         x, y = point[0]
    #         # 更新 x 坐标的最值
    #         if x < min_x:
    #             min_x = x
    #         if x > max_x:
    #             max_x = x

    #     cv2.drawContours(image_np_copy, [contour], 0, (255, 0, 0), 3)
    # # 计算 x 坐标的最值的平均值
    # if min_x != float('inf') and max_x != float('-inf'):
    #     average_x = (min_x + max_x) / 2
    #     print(f"轮廓的 x 坐标最值的平均值为：{average_x}")
    # else:
    #     print("没有找到有效的轮廓")
    
    # if (abs(average_x) - 272) > 1:

    #     print("喷头位置不正确")
        
        
    # else:
    #     print("喷头位置正确")

    




    # # 定义HSV值差异的阈值
    # h_threshold = 100  # 色调差异阈值
    # s_left_threshold = 6000  # 饱和度差异阈值
    # s_right_threshold = 60000  # 饱和度差异阈值
    # v_threshold = 70000 # 亮度差异阈值
 
    # 创建一个与原图像大小相同的边缘图像
    #edges = np.zeros_like(image_np)
    #给识别区域画个方框

    # # 定义正方形区域的坐标
    # x1, y1 = 150,300  # 左上角
    # x2, y2 = 450 ,305 # 右下角
    # cv2.rectangle(image_np_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)  # BGR颜色空间中，(0, 255, 0)代表绿色

    # # 遍历图像中的每个像素
    # for y in range(300, 305):  
    #     for x in range(150, 450):  # 从第二列开始，以便有前一列像素可以比较
    #         # 获取当前像素和相邻像素的HSV值 
    #         current_hsv = image_np[y, x]
    #         last_hsv = image_np[y , x - 1]

    #         # 计算HSV值的差异
    #         h_diff = abs(int(current_hsv[0]) - int(last_hsv[0]))  # 色调差异
    #         s_diff = abs(int(current_hsv[1]) - int(last_hsv[1]))  # 饱和度差异
    #         v_diff = abs(int(current_hsv[2]) - int(last_hsv[2]))  # 亮度差异

    #         # 检查差异是否超过阈值
    #         if (h_diff > h_threshold or s_diff > s_left_threshold  or v_diff > v_threshold) :
    #             # 如果差异超过阈值，则认为是边缘
    #             print(h_diff,s_diff,v_diff)
    #             cv2.circle(image_np_copy, (x, y), 2, (0, 0, 255), -1)  # 红色填充圆



    # 显示图像
    cv2.imshow('Image View', image_np_copy)
    cv2.waitKey(1)


if __name__ == '__main__':
    # 初始化ROS节点
    rospy.init_node('image_view')

    # 订阅摄像头数据
    rospy.Subscriber('usb_cam/image_raw/compressed', CompressedImage, image_callback,queue_size = None,buff_size= 1)


    # 等待回调函数
    rospy.spin()


   