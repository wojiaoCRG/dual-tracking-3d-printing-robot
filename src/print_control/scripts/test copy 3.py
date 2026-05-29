from pymycobot import MyCobotSocket
import time

# 默认使用9000端口
#其中"192.168.11.15"为机械臂IP，请自行输入你的机械臂IP
mc = MyCobotSocket("192.168.247.161",9000)  

start_angle1 = [32, -120, -30, 73, 0, -45]  #代表关节转角，第二个参数增大就抬升
start_angle2 = [29, -132, -30, 73, 0, -45]
stop_angle = [-11, -132, -30, 73, 0, -45]
safe_angle = [-14.0, -120, -30, 73, 0, -45]

# start_coords = [197.6, 34.2, -70, -178.49, -0.59, -17.75]
# stop_coords = [176.0, -94.9, -67, -178.31, 0.29, -54.56]
#连接正常就可以对机械臂进行控制操作
time.sleep(5)

mc.send_angles(start_angle1,8)
time.sleep(3)

mc.send_angles(start_angle2,8)
time.sleep(5.5)
print(f"开始坐标:{mc.get_coords()}")

mc.send_angles(stop_angle,1)
time.sleep(14)  #速度0.008就20s，

# 多次尝试获取坐标
stop_coords = None
for i in range(10):
    stop_coords = mc.get_coords()
    if stop_coords is not None and all(coord is not None for coord in stop_coords):
        break
    time.sleep(0.5)
    print(f"尝试获取坐标 {i+1}/10")
print(f"结束坐标: {stop_coords}")


mc.send_angles(safe_angle,8)
time.sleep(3)

# res = mc.get_angles()
# print(res)