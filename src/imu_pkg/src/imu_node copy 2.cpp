#include "ros/ros.h"
#include "sensor_msgs/Imu.h"
#include "tf/tf.h"
#include "geometry_msgs/Twist.h"
#include <cmath>  // For std::abs and atan2

#include <move_base_msgs/MoveBaseAction.h>
#include <actionlib/client/simple_action_client.h>

typedef actionlib::SimpleActionClient<move_base_msgs::MoveBaseAction> MoveBaseClient;
//tell the action client that we want to spin a thread by default

move_base_msgs::MoveBaseGoal goal;

ros::Publisher vel_pub;
double target_yaw;
bool target_yaw_initialized = false;
int count=0;
int go_times = 0;  //直行次数计数器
//int target_yaw_array[] = {0,90,180,-90,0};  //目标角度数组 

void IMUCallback(sensor_msgs::Imu msg);
int main(int argc, char **argv)
{
    setlocale(LC_ALL, "");
    // 2.初始化 ROS 节点:命名(唯一)
    ros::init(argc, argv, "imu_node");
    ros::NodeHandle n;

    MoveBaseClient ac("move_base", true);//ac、goal对象的定义需要放在最前面第，不然会报错
        //wait for the action server to come up
    while(!ac.waitForServer(ros::Duration(5.0))){
        ROS_INFO("Waiting for the move_base action server to come up");
    }

    //移动到原点开始下一轮循环
    goal.target_pose.header.frame_id = "map";
    goal.target_pose.header.stamp = ros::Time::now();

    goal.target_pose.pose.position.x = 0;
    goal.target_pose.pose.position.y = 0;
    goal.target_pose.pose.orientation.w = 1.0;

    ROS_INFO("初始化回原点");
    ac.sendGoal(goal);
    ac.waitForResult();

    if(ac.getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
        ROS_INFO("返回原点成功");
    else
        ROS_INFO("未能返回原点");

    // 创建 Subscriber 对象，用于接收IMU数据
    ros::Subscriber imu_sub = n.subscribe("/imu/data", 1, IMUCallback);
    
    // 创建 Publisher 对象，用于发布速度命令
    vel_pub = n.advertise<geometry_msgs::Twist>("cmd_vel", 1);
    

    // 主循环，持续监听并处理消息
    ros::Rate r(10);  // 每秒处理10次消息
    while (ros::ok()) {
        r.sleep();
        ros::spinOnce();  // 处理所有收到的消息
    }
    return 0;
}


void IMUCallback(sensor_msgs::Imu msg)
{   

    //正方形轨迹
    if(msg.orientation_covariance[0]<0)
    return;

    tf::Quaternion quaternion(
        msg.orientation.x,
        msg.orientation.y,
        msg.orientation.z,
        msg.orientation.w
    );

    double roll,pitch,yaw;
    tf::Matrix3x3(quaternion).getRPY(roll,pitch,yaw);
    // roll = roll*180/M_PI;
    // pitch = pitch*180/M_PI;
    yaw = yaw*180/M_PI;
    ROS_INFO("朝向= %.0f",yaw);

    //当前角度赋给target_yaw作为初始值
    if (!target_yaw_initialized)
    {
        //初始化目标角度
        target_yaw = yaw + 90;
        target_yaw_initialized = true;
        ROS_INFO("初始化目标角度= %.0f",target_yaw);
    }
    //target_yaw = 10;
    //初始化了，则每直行200mm转90度
    
    else if(abs(abs(target_yaw) - abs(yaw)) <= 3)
    { 
        if (go_times == 3){
            //通过slam地图让小车回原点
            MoveBaseClient ac("move_base", true);//ac、goal对象的定义需要放在最前面第，不然会报错
            //wait for the action server to come up
            while(!ac.waitForServer(ros::Duration(5.0))){
                ROS_INFO("Waiting for the move_base action server to come up");
            }

            ROS_INFO("Sending goal");
            ac.sendGoal(goal);
            ac.waitForResult();

            if(ac.getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
                ROS_INFO("返回原点成功");
            else
                ROS_INFO("未能返回原点");
            go_times = 0;  //直行次数计数器清零
            target_yaw = yaw + 90;
        }
        else{ 
            count++;
            ROS_INFO("abs(target_yaw - yaw)= %.0f,count=%d",abs(target_yaw - yaw),count);
            if(count==100)  //100次循环10s，线速度20mm/s，相乘得200mm路程
            {
                target_yaw = target_yaw + 90;

                if(target_yaw>  180)
                {
                    target_yaw-=360;
                }
                count=0;
                go_times++;
                ROS_INFO("直行次数= %d",go_times);
                ROS_INFO("目标角度= %.0f",target_yaw);
            } 
        }
    
        
        
    }

    //通过差值来驱动小车
    double diff_angle = target_yaw - yaw;  
    geometry_msgs::Twist vel_cmd;
    vel_cmd.linear.x = 0.02;  //线速度为0.02m/s
    //直行时允许左右转微调角度
    if(abs(abs(target_yaw) - abs(yaw)) <=10 && abs(diff_angle)< 260){     //abs(diff_angle)< 260是为了解决当target_yaw=130-140度时，yaw=140-130度，然后相差10度，进入直行微调
        
        if(target_yaw >= 170 && target_yaw <= 180 && yaw < 0){   //防止无法右微调，所以-360
            vel_cmd.angular.z = int(diff_angle - 360 )* 0.02;
        }
        else if(target_yaw >= -180 && target_yaw <= -170 && yaw > 0){   //防止无法左微调，所以+360
            vel_cmd.angular.z = int(diff_angle + 360 )* 0.02;
        }      
        else{
            vel_cmd.angular.z = int(diff_angle )* 0.02;

        }

    }
    //大方向转弯设置为左转
    else{
        vel_cmd.angular.z = fabs(diff_angle )*10;
    }
    
    ROS_INFO("diff_angle = %d",int(diff_angle));
    vel_pub.publish(vel_cmd);
    
}

    

