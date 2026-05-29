from pymycobot import ElephantRobot

if __name__=='__main__':
    "连接机器人服务器"
    elephant_client = ElephantRobot("192.168.195.179", 5001)

    "开启TCP通信"
    elephant_client.start_client()

    "打印机器人当前6个关节角度信息"   
    elephant_client.get_angles()

    "等待机器人运动到目标位置再执行后续指令"
    elephant_client.command_wait_done()