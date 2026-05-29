#include "ros/ros.h"
#include "sensor_msgs/Imu.h"
#include "tf/tf.h"
#include "geometry_msgs/Twist.h"
#include <cmath>  // For std::abs and atan2

ros::Publisher vel_pub;
double target_yaw;
bool target_yaw_initialized = false;
int count=0;

void IMUCallback(sensor_msgs::  Imu msg)
{
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

    ROS_INFO("朝向= %.2f",yaw);

    //当前角度赋给target_yaw作为初始值
    if (!target_yaw_initialized)
    { 
        target_yaw= yaw +90;
        if(target_yaw>=180)
        {
            target_yaw-=360;
        }
        target_yaw_initialized = true;
        ROS_INFO("初始化目标角度= %.2f",target_yaw);

    }
    //target_yaw = 10;
    //初始化了，则每直行200mm转90度

    else if((fabs(abs(target_yaw) - fabs(yaw)) <= 3) && ((fabs(target_yaw - yaw)< 270) || (fabs(target_yaw - yaw) >348)))
    {
        count++;
        ROS_INFO("abs(target_yaw - yaw)= %.0f,count=%d",abs(target_yaw - yaw),count);
        if(count==100)  //40次循环4s，线速度50mm/s，相乘得200mm路程
        {
            target_yaw+=90;
            if(target_yaw>=180)
            {
                target_yaw-=360;
            }
            count=0;
            ROS_INFO("目标角度= %.2f",target_yaw);
        }
    }
    
    //通过差值来驱动小车
    double diff_angle = target_yaw - yaw;  
    geometry_msgs::Twist vel_cmd;
    vel_cmd.linear.x = 0.0;  //线速度为0.05m/s
    //直行时允许左右转微调角度
    // ROS_INFO("%d",int(abs(abs(target_yaw) - abs(yaw)) <=10 && (abs(diff_angle)< 270 || abs(diff_angle) >348)));
    // ROS_INFO("%d",int((abs(abs(target_yaw) - abs(yaw)) <=10) && (abs(diff_angle)< 270 || abs(diff_angle) >348)));
    // ROS_INFO("%d",int(abs(abs(target_yaw) - abs(yaw)) <=10 && (abs(diff_angle)< 270)));
    // ROS_INFO("%d",int(abs(abs(target_yaw) - abs(yaw)) <=10 ));
    // ROS_INFO("%d",int(abs(abs(target_yaw) - abs(yaw))));
    if((fabs(abs(target_yaw) - fabs(yaw)) <= 5) && ((fabs(target_yaw - yaw)< 270) || (fabs(target_yaw - yaw) >348))){
    // if(fabs(target_yaw - yaw) <= 5){

        if(target_yaw >= 170 && target_yaw <= 180 && yaw < 0){   //防止无法右微调，所以-360
            ROS_INFO("1");
            vel_cmd.angular.z = (diff_angle - 360 )* 0.0;
        }
        else if(target_yaw >= -180 && target_yaw <= -170 && yaw > 0){   //防止无法左微调，所以+360
            ROS_INFO("2");
            vel_cmd.angular.z = (diff_angle + 360 )* 0.0;
        }      
        else{
            ROS_INFO("3");
            vel_cmd.angular.z = (diff_angle )* 0.0;  
        }

        ROS_INFO("diff_angle = %.2f",(diff_angle));
    }
    // 大方向转弯设置为左转
    else{
        vel_cmd.angular.z = 0;
        ROS_INFO("target_yaw-yaw = %d",int(target_yaw-yaw));
    }
    
    vel_pub.publish(vel_cmd);
}

int main(int argc, char **argv)
{
    setlocale(LC_ALL, "");
    // 2.初始化 ROS 节点:命名(唯一)
    ros::init(argc, argv, "imu_test");
    ros::NodeHandle n;

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
