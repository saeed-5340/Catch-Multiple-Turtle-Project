# Catch Multiple Turtles — ROS 2 Turtlesim Project

A ROS 2 project that simulates a "hunter" turtle autonomously chasing and catching randomly spawned enemy turtles in the Turtlesim environment.

---

## Overview

This project demonstrates core ROS 2 concepts including publishers, subscribers, service clients, timers, and callbacks. A main controller node (`control_robot`) drives `turtle1` to hunt down enemy turtles that are periodically spawned at random positions. When the hunter gets close enough to an enemy, the enemy is killed via the `/kill` service.

---

## Features

- **Autonomous hunting** — `turtle1` continuously navigates toward the nearest enemy turtle using proportional control (P-controller) for both linear and angular velocity.
- **Dynamic spawning** — A new enemy turtle is spawned every second at a random position and orientation.
- **Closest-target selection** — The hunter always prioritizes the nearest enemy turtle.
- **Auto-kill on catch** — When the hunter reaches within `0.5` units of an enemy, that turtle is removed from the simulation.
- **Pose tracking** — All turtle poses (hunter + enemies) are tracked via `/pose` topic subscriptions.

---

## Project Structure

```
catch_multiple_turtle/
├── catch_multiple_turtle/
│   └── control_robot.py       # Main controller node
├── launch/
│   └── catch_turtle.launch.py # Launch file
├── package.xml
└── setup.py
```

---

## Nodes

### `control_robot` (`ControlRobot`)

| Role | Details |
|---|---|
| **Package** | `catch_multiple_turtle` |
| **Executable** | `control_robot` |
| **Node name** | `control_my_robot` |

#### Publishers
| Topic | Type | Description |
|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/Twist` | Velocity commands for the hunter turtle |

#### Subscribers
| Topic | Type | Description |
|---|---|---|
| `/turtle1/pose` | `turtlesim/Pose` | Pose of the hunter turtle |
| `/<enemy_name>/pose` | `turtlesim/Pose` | Pose of each spawned enemy turtle |

#### Service Clients
| Service | Type | Description |
|---|---|---|
| `/spawn` | `turtlesim/Spawn` | Spawns a new enemy turtle |
| `/kill` | `turtlesim/Kill` | Removes a caught enemy turtle |

#### Timers
| Period | Callback | Description |
|---|---|---|
| 1.0 s | `launch_spawner` | Spawns a new enemy turtle |
| 0.2 s | `hunt_enemy` | Updates hunter velocity toward the nearest enemy |

---

## Control Logic

The hunter uses a simple **proportional controller**:

- **Angular velocity** — Proportional to the angle difference between the hunter's heading and the direction toward the target.
- **Linear velocity** — Fixed forward speed (`2.5 × kp_linear = 4.25`) when the target is farther than `0.5` units away.
- **Angle wrapping** — `theta_diff` is normalized to `[-π, π]` to prevent spinning in the wrong direction.
- **Kill threshold** — When distance to target `< 0.5`, velocity is zeroed and a `/kill` service call is issued.

```
kp_linear  = 1.7   →  linear.x  = 4.25
kp_angular = 5.0   →  angular.z = 5.0 × theta_diff
```

---

## Prerequisites

- **ROS 2** (Humble / Iron / Rolling recommended)
- **turtlesim** package  
  ```bash
  sudo apt install ros-<distro>-turtlesim
  ```
- Python 3

---

## Installation

1. Clone the repository into your ROS 2 workspace:
   ```bash
   cd ~/ros2_ws/src
   git clone <repository_url> catch_multiple_turtle
   ```

2. Build the package:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select catch_multiple_turtle
   ```

3. Source the workspace:
   ```bash
   source install/setup.bash
   ```

---

## Usage

### Launch everything at once (recommended)

```bash
ros2 launch catch_multiple_turtle catch_turtle.launch.py
```

This starts both the `turtlesim_node` and the `control_robot` node together.

### Run nodes individually

**Terminal 1 — Start turtlesim:**
```bash
ros2 run turtlesim turtlesim_node
```

**Terminal 2 — Start the controller:**
```bash
ros2 run catch_multiple_turtle control_robot
```

---

## How It Works

1. On startup, `turtle1` (the hunter) is already present in the simulation.
2. Every **1 second**, a new enemy turtle is spawned at a random `(x, y, θ)` within the simulation bounds.
3. Every **0.2 seconds**, the hunter computes the distance to all known enemies, selects the closest, and publishes a `Twist` command to steer toward it.
4. When the hunter comes within **0.5 units** of an enemy, it stops, calls `/kill` to remove the enemy, and removes it from the internal pose dictionary.
5. The cycle repeats indefinitely — enemies accumulate faster than they are caught, increasing the challenge over time.

---

## Key ROS 2 Concepts Demonstrated

| Concept | Where Used |
|---|---|
| Publisher | `/turtle1/cmd_vel` velocity commands |
| Subscriber | Pose tracking for all turtles |
| Service Client (async) | `/spawn` and `/kill` |
| Timer | Periodic spawning and hunting loops |
| `partial()` callbacks | Passing `name` into `enemy_pose_callback` |
| `add_done_callback` | Non-blocking async service calls |

---

## Tuning

You can adjust the following constants in `control_robot.py` to change behaviour:

| Constant | Default | Effect |
|---|---|---|
| `kp_linear` | `1.7` | Base forward speed multiplier |
| `kp_angular` | `5.0` | Turn rate aggressiveness |
| `twist.linear.x` | `2.5 × kp_linear` | Actual forward speed |
| Kill threshold | `0.5` | Catch distance in simulation units |
| Spawn timer | `1.0 s` | How often a new enemy appears |
| Hunt timer | `0.2 s` | Control loop frequency |

---

## License

MIT License — free to use, modify, and distribute.
