from pymycobot import ElephantRobot
import signal
import sys

# mycobot pro 600 直线及往复代码
# 机器人的IP地址和端口号
robot_ip = "192.168.195.179"
port = 5001

# 创建ElephantRobot类的实例
robot = ElephantRobot(robot_ip, port)

# 连接机器人服务器
robot.start_client()

# 获取当前的笛卡尔坐标并存储在变量中
start_coords = [308.2 ,-21.08 ,59.39,178.62,-0.44,-7.22]
current_x = start_coords[0]  # 当前X坐标
current_y = start_coords[1]  # 当前Y坐标
current_z = start_coords[2]  # 当前Z坐标

stop_coords = [409.75 ,-27.47 ,59.39,178.62,-0.44,-7.22]

# 定义移动的距离，例如沿X轴移动100mm，沿Z轴移动0.4mm
#distance_x = 103  # 沿X轴移动的距离
step_z = 0.4  # 沿Z轴每次移动的距离

# 定义运动速度
speed = 480

# 发送直线运动指令并等待完成的函数
def move_and_wait(x, y, z):
    global current_x, current_y, current_z  # 声明全局变量
    robot.write_coords([current_x + x, current_y + y, current_z + z,
                        start_coords[3], start_coords[4], start_coords[5]], speed)
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
    
    robot.write_coords(start_coords,speed)
    robot.command_wait_done()

    # 沿X轴和Y轴交替移动
    z_movement = 0  # 记录z轴的总移动量
    while z_movement < 13:  # 直到Y轴移动总量达到20mm
        #move_and_wait(distance_x, 0, 0)  # 沿X轴正向移动
        robot.write_coords([stop_coords[0],stop_coords[1],stop_coords[2],stop_coords[3]+z_movement,stop_coords[4],stop_coords[5]],speed)
        robot.command_wait_done()

        move_and_wait(0,0,step_z)      # 沿z轴正向移动0.4mm
        z_movement += step_z              # 更新z轴总移动量

        if z_movement >= 13:
            break  # 如果Y轴移动量达到20mm，退出循环

        #move_and_wait(-distance_x, 0, 0)  # 沿X轴负向移动回原X位置
        robot.write_coords([start_coords[0],start_coords[1],start_coords[2],start_coords[3]+z_movement,start_coords[4],start_coords[5]],speed)
        robot.command_wait_done()

        move_and_wait(0,0,step_z)    
        z_movement += step_z               # 更新Y轴总移动量（回退）

    move_and_wait(30, 0, 60)
    
except KeyboardInterrupt:
    safe_shutdown()
    
finally:
    # 确保无论如何都会尝试关闭连接
    try:
        robot.stop_client()
    except:
        pass