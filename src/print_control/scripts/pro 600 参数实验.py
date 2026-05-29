from pymycobot import ElephantRobot
import signal
import sys

# mycobot pro 600 直线及往复代码
# 机器人的IP地址和端口号
robot_ip = "192.168.10.179"
port = 5001

# 创建ElephantRobot类的实例
robot = ElephantRobot(robot_ip, port)

# 连接机器人服务器
robot.start_client()


# 获取当前的笛卡尔坐标并存储在变量中
#start_coords = [310.14,-20,59.4,178.62,-0.44,-7.22] x正方向起点
#start_coords = [350.14, 1.39, 58.8, 178.62, -0.44, -7.22]  #单道起点，层高0.4的z轴坐标为59.1
start_coords = [315.14, 1.39, 58.5, 178.62, -0.44, -7.22]  #多道起点
robot.write_coords(start_coords, 800)
robot.command_wait_done()
print("移动至初始点")

# stop_coords = [413.14, 5, 58.8, 178.62, -0.44, -7.22]  #单道终点，层高0.4的z轴坐标为58.8
# robot.write_coords(stop_coords, 480)
# robot.command_wait_done()
# print("移动至单道终点")

# stop_coords = [436.14,1.39,100.1,178.62,-0.44,-7.22]  #抬升终点
# robot.write_coords(stop_coords, 480)
# robot.command_wait_done()
# print("移动至抬升终点")

# # 关闭与机器人的TCP连接(初始点测试)
# robot.stop_client()

current_coords = robot.get_coords()
current_x = current_coords[0]  # 当前X坐标
current_y = current_coords[1]  # 当前Y坐标
current_z = current_coords[2]  # 当前Z坐标

# 定义移动的距离，例如沿X轴移动100mm，沿Z轴移动0.4mm
#distance_x = 105  # 沿X轴移动的距离（拉伸式样）
distance_x = 105  # 沿X轴移动的距离(弯曲式样)
step_z = 0.8 # 沿Z轴每次移动的距离
z_movement = 0  # 记录z轴的总移动量

# 定义运动速度
speed = 660

# 发送直线运动指令并等待完成的函数
def move_and_wait(x, y, z):
    global current_x, current_y, current_z  # 声明全局变量
    # if z_movement <= 0.8:
    #     speed = 300
    # else:
    #     speed = 300
    robot.write_coords([current_x + x, current_y + y, current_z + z,
                        current_coords[3], current_coords[4], current_coords[5]], speed)
    robot.command_wait_done()
    current_x += x  # 更新当前X坐标
    current_y += y  # 更新当前Y坐标
    current_z += z  # 更新当前Z坐标

# 安全关闭机器人的函数
def safe_shutdown(signum=None, frame=None):
    print("\n检测到用户中断，正在安全关闭机器人连接...")
    try:
        move_and_wait(30, 0, 60)  # 执行安全移动
        robot.stop_client()
        print("机器人连接已安全关闭")
    except Exception as e:
        print(f"关闭过程中出现错误: {e}")
    sys.exit(0)

# 注册信号处理函数
signal.signal(signal.SIGINT, safe_shutdown)

try:
    # 沿X轴和Y轴交替移动
    while z_movement < 13:  # 直到Y轴移动总量达到20mm
        move_and_wait(distance_x, 0, 0)  # 沿X轴正向移动
        move_and_wait(0,0,step_z)      # 沿z轴正向移动0.4mm
        z_movement += step_z              # 更新z轴总移动量

        if z_movement >= 13:
            break  # 如果Y轴移动量达到20mm，退出循环

        move_and_wait(-distance_x, 0, 0)  # 沿X轴负向移动回原X位置
        move_and_wait(0,0,step_z)      # 沿Y轴负向移动回原Y位置
        z_movement += step_z               # 更新Y轴总移动量（回退）

    stop_coords = [400.14,31.39,130.1,178.62,-0.44,-7.22]  #抬升终点
    robot.write_coords(stop_coords, 480)
    robot.command_wait_done()
    print("移动至抬升终点")
    
except KeyboardInterrupt:
    safe_shutdown()
    
finally:
    # 确保无论如何都会尝试关闭连接
    try:
        robot.stop_client()
    except:
        pass