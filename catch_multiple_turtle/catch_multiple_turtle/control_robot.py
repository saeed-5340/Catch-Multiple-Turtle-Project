#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn
from functools import partial
from turtlesim.srv import Kill
import random
import math


class ControlRobot(Node):
    def __init__(self):
        super().__init__('control_my_robot')
        self.turtle_poses = {'turtle1' : None}
        self.count = 1
        self.name = None

        self.cmd_val = self.create_publisher(Twist,'/turtle1/cmd_vel',10)

        self.subs = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        self.create_timer(1.0, self.launch_spawner)
        
        self.create_timer(0.2,self.hunt_enemy)

    def pose_callback(self, msg):
        self.turtle_poses['turtle1'] = msg

    def enemy_pose_callback(self,msg,name):
        self.turtle_poses[name] = msg
        # if  name == self.name:
        #     self.get_logger().info(f"Enemy {name} pose: x={msg.x}, y={msg.y}, theta={msg.theta}")



    def launch_spawner(self):
        self.count +=1
        name = f'turtle{self.count}'
        self.name = name
        claint = self.create_client(Spawn, '/spawn')
        while not claint.wait_for_service(1.0):
            self.get_logger().warn("Waiting for service...")
        request = Spawn.Request()
        request.x = random.uniform(0.0,10.0)
        request.y = random.uniform(0.0,10.0)
        request.theta = random.uniform(0.0, 2 * math.pi)
        request.name = name
        msg = Pose()
        msg.x = request.x
        msg.y = request.y
        msg.theta = request.theta
        future = claint.call_async(request)
        # rclpy.spin_until_future_complete(self, future)
        future.add_done_callback(partial(self.spawn_turtle_callback))

        self.create_subscription(
            Pose, f'/{name}/pose',partial(self.enemy_pose_callback,name=name),10)
        # self.create_subscription(
        #     Pose, f'/{name}/pose',lambda msg: self.enemy_pose_callback(msg,name),10)
        

    def spawn_turtle_callback(self, future):
        try:
            future.result()
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

    def hunt_enemy(self):
        target_enemy = None
        hunter_pose = None
        closest_enemy = float('Inf')
        if self.turtle_poses['turtle1'] is None:
            return

        if self.name is None:
            return

        if len(self.turtle_poses) <= 1:
            self.get_logger().info("No enemy to hunt.")
            return

        hunter_pose = self.turtle_poses['turtle1']
        for name, pose in self.turtle_poses.items():
            if name == 'turtle1' or pose is None:
                continue
            distance = math.sqrt((hunter_pose.x - pose.x) ** 2 + (hunter_pose.y - pose.y) ** 2)
            if distance < closest_enemy:
                closest_enemy = distance
                target_enemy = pose
                target_enemy_name = name

        if target_enemy is None:
            return
        
        if closest_enemy > 0.5: 
            dx = (target_enemy.x - hunter_pose.x)
            dy = (target_enemy.y - hunter_pose.y)
            kp_linear = 1.7
            kp_angular = 5.0
            angle = math.atan2(dy, dx)
            theta_diff = (angle - hunter_pose.theta)
            self.get_logger().info(f"Target angle:{angle})")
            twist = Twist()
            twist.linear.x = 2.5*kp_linear
            if theta_diff > math.pi:
                theta_diff -= 2*math.pi
            elif theta_diff< -math.pi:
                theta_diff+= 2*math.pi
            twist.angular.z = kp_angular*theta_diff
        else:
            twist = Twist()
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        self.cmd_val.publish(twist)


        if closest_enemy < 0.5:
            cnt = self.create_client(Kill, '/kill')
            while not cnt.wait_for_service(1.0):
                self.get_logger().warn("Waiting for service...")

            req = Kill.Request()
            req.name = target_enemy_name
            future = cnt.call_async(req)
            future.add_done_callback(self.kill_enemy_callback)
            self.turtle_poses.pop(target_enemy_name)

    def kill_enemy_callback(self, future):
        try:
            future.result()
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")
        





def main(args=None):
    rclpy.init(args=args)
    node  = ControlRobot()
    rclpy.spin(node)
    rclpy.shutdown()




if __name__ == '__main__':
    main()