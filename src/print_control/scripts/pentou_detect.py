# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import CompressedImage
import cv2
import numpy as np



def image_callback(msg):

    # 使用cv_bridge的compressed_imgmsg_to_cv2方法将CompressedImage消息转换为OpenCV图像
    np_arr = np.frombuffer(msg.data, np.uint8)
    image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # 读取目标图像和二值化模板图像
    template_image_path = "/home/crg/桌面/pentou.png"  # 二值化模板图像路径

    target_image = image_np
    template_image = cv2.imread(template_image_path, 0)  # 以灰度模式读取

    # 将目标图像转换为灰度图
    target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

    # 二值化目标图像
    #_, target_binary = cv2.threshold(target_gray, 127, 255, cv2.THRESH_BINARY)
    dst = cv2.Canny(target_gray , threshold1, threshold2, apertureSize=3, L2gradient=False)

    cv2.imshow("target_binary", target_binary)
    cv2.waitKey(1)

    # 获取模板图像的轮廓（喷头模板的长138宽185）
    template_contour, _ = cv2.findContours(template_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 获取模板图像的第一个轮廓(只有一个轮廓)
    contour = template_contour[0]

    # 将掩码应用到目标二值化图像上
    matched_region = cv2.bitwise_and(target_binary, target_binary, mask=match_mask)
    
    # 计算匹配区域与模板的匹配度
    match_result = cv2.matchTemplate(matched_region, template_image, cv2.TM_CCOEFF_NORMED)
    
    # 获取匹配度最高的点的位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)
    
    # 设置一个阈值来判断匹配程度
    if max_val > 0.1:  # 可以根据实际情况调整阈值
        # 在目标图像上绘制匹配的轮廓
        cv2.drawContours(target_image, [contour], -1, (0, 0, 255), 3)  # 红色显示
    # 显示结果
    cv2.imshow("Matched Shapes", target_image)
    cv2.waitKey(1)


if __name__ == '__main__':
    # 初始化ROS节点
    rospy.init_node('image_view')

    # 订阅摄像头数据
    rospy.Subscriber('usb_cam/image_raw/compressed', CompressedImage, image_callback)


    # 等待回调函数
    rospy.spin()


