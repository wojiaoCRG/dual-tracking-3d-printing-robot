#! /usr/bin/python3.8
# coding=utf-8

from pymycobot.mycobot import MyCobot
from pymycobot.genre import Coord
from pymycobot.genre import Angle
import time
import rospy
import math
import numpy as np

mc = MyCobot('192.168.227.161', 9000)

class ArcPrinter:
    def __init__(self):
        self.mc = mc
        self.speed = 20  # 默认运动速度
        self.model = 0   # 运动模式：0-关节运动，1-直线运动
        
    def go_home(self):
        """回到初始位置"""
        home_coords = [195, -37.3, -67, -177.85, -1.3, 136.44]
        print("回到初始位置...")
        mc.send_coords(home_coords, self.speed, self.model)
        time.sleep(3)
        
    def calculate_arc_points(self, center, radius, start_angle, end_angle, num_points):
        """
        计算四分之一圆弧的路径点
        
        参数:
            center: 圆心坐标 [x, y, z]
            radius: 圆弧半径 (mm)
            start_angle: 起始角度 (弧度)
            end_angle: 结束角度 (弧度)
            num_points: 路径点数量
            
        返回:
            points: 圆弧路径点列表
        """
        points = []
        
        # 角度序列
        angles = np.linspace(start_angle, end_angle, num_points)
        
        for angle in angles:
            # 计算圆弧上的点坐标
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = center[2]  # z轴保持不变
            
            # 保持其他坐标轴姿态不变
            rx = center[3] if len(center) > 3 else -177.85
            ry = center[4] if len(center) > 4 else -1.3
            rz = center[5] if len(center) > 5 else 136.44
            
            point = [x, y, z, rx, ry, rz]
            points.append(point)
            
        return points
    
    def move_to_start(self, start_point, approach_height=10):
        """
        移动到圆弧起点（带安全高度）
        
        参数:
            start_point: 起点坐标
            approach_height: 安全高度 (mm)
        """
        # 先抬升到安全高度
        safe_point = start_point.copy()
        safe_point[2] += approach_height
        
        print(f"移动到安全高度: {safe_point}")
        mc.send_coords(safe_point, self.speed, 1)  # 直线运动到安全高度
        time.sleep(2)
        
        # 下降到起点
        print(f"下降到起点: {start_point}")
        mc.send_coords(start_point, 10, 1)  # 慢速下降
        time.sleep(1)
    
    def print_quarter_arc(self, center, radius, plane='xy', direction='cw', num_points=20):
        """
        打印四分之一圆弧
        
        参数:
            center: 圆心坐标 [x, y, z, rx, ry, rz]
            radius: 圆弧半径 (mm)
            plane: 圆弧平面 ('xy', 'xz', 'yz')
            direction: 方向 ('cw'-顺时针, 'ccw'-逆时针)
            num_points: 路径点数量
        """
        # 根据平面和方向确定角度范围
        if plane == 'xy':
            if direction == 'cw':
                start_angle = 0  # 从X轴正方向开始
                end_angle = -math.pi/2  # 顺时针90度
            else:
                start_angle = 0
                end_angle = math.pi/2  # 逆时针90度
        elif plane == 'xz':
            # 在XZ平面画弧（需要调整实现）
            print("XZ平面圆弧暂未实现，使用XY平面")
            return self.print_quarter_arc(center, radius, 'xy', direction, num_points)
        else:  # yz平面
            print("YZ平面圆弧暂未实现，使用XY平面")
            return self.print_quarter_arc(center, radius, 'xy', direction, num_points)
        
        # 计算圆弧路径点
        arc_points = self.calculate_arc_points(center, radius, start_angle, end_angle, num_points)
        
        print(f"开始打印四分之一圆弧，半径: {radius}mm, 点数: {len(arc_points)}")
        
        # 移动到起点
        self.move_to_start(arc_points[0])
        
        # 打印圆弧
        for i, point in enumerate(arc_points):
            print(f"移动到点 {i+1}/{len(arc_points)}: {point[:3]}")  # 只打印位置坐标
            
            # 使用直线运动模式保证轨迹平滑
            mc.send_coords(point, self.speed, 1)
            
            # 根据距离计算等待时间（确保运动完成）
            if i > 0:
                # 计算与上一个点的距离
                prev_point = arc_points[i-1]
                distance = math.sqrt(sum((point[j]-prev_point[j])**2 for j in range(3)))
                wait_time = distance / self.speed + 0.1  # 基础等待时间
            else:
                wait_time = 1.0
                
            time.sleep(max(wait_time, 0.5))  # 最小等待0.5秒
        
        print("圆弧打印完成")
        
        # 抬升喷头
        end_point = arc_points[-1].copy()
        end_point[2] += 10
        print("抬升喷头...")
        mc.send_coords(end_point, self.speed, 1)
        time.sleep(1)
    
    def adaptive_speed_arc_print(self, center, radius, base_speed=20, 
                                min_speed=10, max_speed=30, num_points=30):
        """
        自适应速度的圆弧打印（基于曲率调整速度）
        
        参数:
            center: 圆心坐标
            radius: 圆弧半径
            base_speed: 基准速度
            min_speed: 最小速度
            max_speed: 最大速度
            num_points: 路径点数量
        """
        # 计算圆弧路径点（完整90度）
        arc_points = self.calculate_arc_points(center, radius, 0, math.pi/2, num_points)
        
        # 移动到起点
        self.move_to_start(arc_points[0])
        
        print("开始自适应速度圆弧打印...")
        
        for i in range(len(arc_points)):
            # 根据曲率调整速度（小半径圆弧用较慢速度）
            curvature = 1.0 / radius if radius > 0 else 0
            speed_factor = 1.0 / (1.0 + curvature * 5)  # 曲率越大，速度越慢
            
            current_speed = base_speed * speed_factor
            current_speed = max(min_speed, min(max_speed, current_speed))
            
            print(f"点 {i+1}: 曲率={curvature:.3f}, 速度={current_speed:.1f}")
             
            mc.send_coords(arc_points[i], int(current_speed), 1)
            
            # 计算等待时间
            if i > 0:
                distance = math.sqrt(sum((arc_points[i][j]-arc_points[i-1][j])**2 for j in range(3)))
                wait_time = distance / current_speed + 0.1
            else:
                wait_time = 0.5
                
            time.sleep(wait_time)
        
        print("自适应速度圆弧打印完成")

def main():
    # 创建圆弧打印机对象
    arc_printer = ArcPrinter()
    
    # 回到初始位置
    arc_printer.go_home()
    
    try:
        # 初始化ROS节点
        rospy.init_node('arc_printing_node')
        
        # 获取当前坐标作为参考
        current_coords = mc.get_coords()
        time.sleep(0.1)
        
        if current_coords:
            print(f"当前坐标: {current_coords}")
            
            # 以当前位置为参考点，设置圆心（稍微偏移避免碰撞）
            center_point = current_coords.copy()
            center_point[0] += 50  # X方向偏移
            center_point[1] += 0   # Y方向不变
            
            # 设置圆弧半径
            radius = 30  # 30mm半径
            
            print(f"圆心坐标: {center_point[:3]}")
            print(f"圆弧半径: {radius}mm")
            
            # 方法1：标准四分之一圆弧打印
            print("\n=== 方法1: 标准圆弧打印 ===")
            arc_printer.print_quarter_arc(
                center=center_point,
                radius=radius,
                plane='xy',
                direction='ccw',  # 逆时针
                num_points=15
            )
            
            time.sleep(2)
            
            # 回到安全位置
            arc_printer.go_home()
            time.sleep(1)
            
            # # 方法2：自适应速度圆弧打印
            # print("\n=== 方法2: 自适应速度圆弧打印 ===")
            # # 调整圆心位置
            # center_point[0] += 60
            
            # arc_printer.adaptive_speed_arc_print(
            #     center=center_point,
            #     radius=radius,
            #     base_speed=20,
            #     min_speed=10,
            #     max_speed=30,
            #     num_points=20
            #)
            
        else:
            print("无法获取当前坐标，使用默认坐标")
            # 使用默认坐标
            default_center = [200, -30, -60, -177.85, -1.3, 136.44]
            arc_printer.print_quarter_arc(default_center, 30, 'xy', 'ccw', 15)
        
        # 最终回到初始位置
        arc_printer.go_home()
        print("所有打印任务完成！")
        
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        # 确保回到安全位置
        arc_printer.go_home()

if __name__ == '__main__':
    main()