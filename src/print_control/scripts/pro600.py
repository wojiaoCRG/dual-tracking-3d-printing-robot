from pymycobot import ElephantRobot

# mycobot pro 600 直线及往复代码
# 机器人的IP地址和端口号
robot_ip = "192.168.118.179"
port = 5001

# 创建ElephantRobot类的实例
robot = ElephantRobot(robot_ip, port)

# 连接机器人服务器
robot.start_client()

# 获取当前的笛卡尔坐标并存储在变量中
current_coords = robot.get_coords()
current_x = current_coords[0]  # 当前X坐标
current_y = current_coords[1]  # 当前Y坐标
current_z = current_coords[2]  # 当前Z坐标

# 定义移动的距离，例如沿X轴移动100mm，沿Y轴移动0.4mm
distance_x = 100  # 沿X轴移动的距离
step_y = 0.4  # 沿Y轴每次移动的距离

# 定义运动速度
speed = 2000

# 发送直线运动指令并等待完成的函数
def move_and_wait(x, y, z):
    global current_x, current_y, current_z  # 声明全局变量
    robot.write_coords([current_x + x, current_y + y, current_z + z,
                        current_coords[3], current_coords[4], current_coords[5]], speed)
    robot.command_wait_done()
    current_x += x  # 更新当前X坐标
    current_y += y  # 更新当前Y坐标
    current_z += z  # 更新当前Z坐标

# 沿X轴和Y轴交替移动
y_movement = 0  # 记录Y轴的总移动量
while y_movement < 20:  # 直到Y轴移动总量达到20mm
    move_and_wait(distance_x, 0, 0)  # 沿X轴正向移动
    move_and_wait(0, step_y, 0)      # 沿Y轴正向移动0.4mm
    y_movement += step_y              # 更新Y轴总移动量

    if y_movement >= 20:
        break  # 如果Y轴移动量达到20mm，退出循环

    move_and_wait(-distance_x, 0, 0)  # 沿X轴负向移动回原X位置
    move_and_wait(0, -step_y, 0)      # 沿Y轴负向移动回原Y位置
    y_movement -= step_y               # 更新Y轴总移动量（回退）

# 关闭与机器人的TCP连接
robot.stop_client()
