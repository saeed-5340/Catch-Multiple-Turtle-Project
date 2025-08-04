from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()

    tartle_control_node = Node(
        package="catch_multiple_turtle",
        executable="control_robot",
    )

    turtlesim_node = Node(
        package="turtlesim",
        executable = "turtlesim_node",
    )

    ld.add_action(tartle_control_node)
    ld.add_action(turtlesim_node)

    return ld