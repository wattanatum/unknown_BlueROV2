# unknown_BlueROV2

<p align="center">
  <img src="assets/bluerov2_drive.gif" alt="BlueROV2 Drive" width="800"/>
</p>

BlueROV2 underwater robot simulation project using **ROS 2 Jazzy**, **Gazebo Harmonic**, **SLAM Toolbox**, **Nav2**, and **robot_localization EKF**.

This project demonstrates:

* BlueROV2 underwater simulation in Gazebo Harmonic
* ROS 2 bridge from Gazebo to ROS 2
* DVL, IMU, depth, odometry, and 2D lidar integration
* EKF localization using `robot_localization`
* 2D lidar mapping with SLAM Toolbox
* Saved-map navigation with Nav2
* AMCL localization
* Nav2 obstacle avoidance and recovery behavior
* `/cmd_vel` to BlueROV2 thruster control
* Automatic depth control
* Custom underwater Gazebo world and BlueROV2 model

---

## System Requirements

Tested with:

* Ubuntu 24.04
* ROS 2 Jazzy
* Gazebo Harmonic
* SLAM Toolbox
* Nav2
* robot_localization
* ros_gz_bridge
* RViz2
* Python 3

---

## Repository Structure

```text
unknown_bluerov2_ws/
├── README.md
├── .gitignore
├── assets/
│   ├── bluerov2_drive.gif
│   ├── bluerov2_mapping.gif
│   └── bluerov2_navigation.gif
└── src/
    ├── bluerov2_gz/
    │   ├── models/
    │   │   └── bluerov2/
    │   └── worlds/
    │       ├── bluerov2_underwater.world
    │       ├── bluerov2_heavy_underwater.world
    │       └── bluerov2_ping.world
    ├── unknown_bluerov2_bringup/
    │   ├── launch/
    │   │   ├── gazebo.launch.py
    │   │   └── bridge.launch.py
    │   ├── package.xml
    │   └── setup.py
    ├── unknown_bluerov2_control/
    │   ├── launch/
    │   │   ├── depth_control.launch.py
    │   │   ├── sensor_control_ekf.launch.py
    │   │   ├── sensor_fusion_inputs.launch.py
    │   │   └── stuck_recovery.launch.py
    │   ├── unknown_bluerov2_control/
    │   │   ├── cmd_vel_thruster_mixer.py
    │   │   ├── depth_thruster_controller.py
    │   │   ├── odom_to_depth_pose.py
    │   │   ├── odom_to_dvl_twist.py
    │   │   └── bluerov2_stuck_recovery.py
    │   ├── package.xml
    │   └── setup.py
    └── unknown_bluerov2_nav/
        ├── config/
        │   ├── ekf_dvl_imu_depth.yaml
        │   ├── nav2_params.yaml
        │   └── slam_toolbox.yaml
        ├── launch/
        │   ├── ekf_dvl_imu_depth.launch.py
        │   ├── nav2_slam.launch.py
        │   ├── slam_ekf.launch.py
        │   ├── static_tf.launch.py
        │   └── tf_with_odom.launch.py
        ├── maps/
        │   ├── bluerov2_slam_map.yaml
        │   └── bluerov2_slam_map.pgm
        ├── unknown_bluerov2_nav/
        │   └── odom_tf_publisher.py
        ├── package.xml
        └── setup.py
```

---

# Clone This Repository

```bash
cd ~
git clone https://github.com/wattanatum/unknown_BlueROV2.git unknown_bluerov2_ws
cd ~/unknown_bluerov2_ws
```

---

# Install Project Dependencies

## ROS 2 Jazzy packages

```bash
sudo apt update

sudo apt install -y \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-slam-toolbox \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-robot-localization \
  ros-jazzy-tf2-ros \
  ros-jazzy-tf2-tools \
  ros-jazzy-rviz2 \
  ros-jazzy-nav-msgs \
  ros-jazzy-geometry-msgs \
  ros-jazzy-sensor-msgs \
  ros-jazzy-std-msgs \
  ros-jazzy-tf2-msgs \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-pip
```

---

# Build ROS 2 Workspace

```bash
cd ~/unknown_bluerov2_ws
colcon build --symlink-install
source install/setup.bash
```

To source automatically every new terminal:

```bash
echo "source ~/unknown_bluerov2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

# Run BlueROV2 Gazebo Simulation

Open a terminal:

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_bringup gazebo.launch.py
```

This launch starts the Gazebo Harmonic underwater simulation with the BlueROV2 model.

Expected Gazebo topics include:

```text
/clock
/scan
/model/bluerov2/odometry
/model/bluerov2/odometry_with_covariance
/world/bluerov2_underwater/dynamic_pose/info
/world/bluerov2_underwater/model/bluerov2/link/base_link/sensor/imu_sensor/imu
```

---

# Run Gazebo to ROS 2 Bridge

Open a new terminal:

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_bringup bridge.launch.py
```

This bridge publishes important ROS 2 topics:

```text
/clock
/imu
/scan
/odom
/tf
```

Check topics:

```bash
ros2 topic list
```

Check odometry:

```bash
ros2 topic echo /odom --once
```

Check scan:

```bash
ros2 topic echo /scan --once
```

---

# TF and Sensor Frames

The BlueROV2 project uses these important frames:

```text
map -> odom -> base_link
base_link -> imu_link
base_link -> dvl_link
base_link -> depth_link
base_link -> laser_link
```

Static sensor transforms:

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_nav static_tf.launch.py
```

If using the combined TF launch:

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_nav tf_with_odom.launch.py
```

Check TF:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link laser_link
ros2 run tf2_ros tf2_echo base_link imu_link
```

---

# EKF Localization

This project uses `robot_localization` to fuse:

* DVL velocity
* IMU orientation / angular velocity
* Depth pose
* Gazebo odometry input

Important topics:

```text
/dvl/twist
/depth
/depth/pose
/imu
/odom
/odometry/filtered
```

Run EKF:

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_nav ekf_dvl_imu_depth.launch.py
```

Check filtered odometry:

```bash
ros2 topic echo /odometry/filtered --once
```

Check EKF TF:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```text
odom -> base_link
```

---

# Full SLAM + EKF + Nav2 Launch

Use this main launch file for the full system:

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_nav slam_ekf.launch.py
```

This launch can start:

* Gazebo bridge
* Static TF
* Sensor conversion nodes
* Depth controller
* EKF localization
* SLAM Toolbox
* Nav2
* Thruster mixer

---

# SLAM Toolbox Mapping

<p align="center">
  <img src="assets/bluerov2_mapping.gif" alt="BlueROV2 Mapping" width="800"/>
</p>

Use this method when creating a new map.

Do **not** run saved-map navigation with AMCL at the same time as SLAM Toolbox mapping.

## Terminal 1: Launch Gazebo

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_bringup gazebo.launch.py
```

## Terminal 2: Launch Bridge

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_bringup bridge.launch.py
```

## Terminal 3: Launch SLAM + EKF

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_nav slam_ekf.launch.py
```

## Terminal 4: Run RViz2

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
rviz2
```

In RViz2, set:

```text
Fixed Frame: map
```

Useful RViz2 displays:

```text
/map
/scan
/tf
/odometry/filtered
/local_costmap/costmap
/global_costmap/costmap
/plan
```

---

# Save SLAM Map

After mapping, save the map:

```bash
cd ~/unknown_bluerov2_ws/src/unknown_bluerov2_nav/maps
ros2 run nav2_map_server map_saver_cli -f bluerov2_slam_map
```

Expected files:

```text
bluerov2_slam_map.yaml
bluerov2_slam_map.pgm
```

Rebuild after saving maps:

```bash
cd ~/unknown_bluerov2_ws
colcon build --packages-select unknown_bluerov2_nav --symlink-install
source install/setup.bash
```

---

# Nav2 Saved-Map Navigation

<p align="center">
  <img src="assets/bluerov2_navigation.gif" alt="BlueROV2 Navigation" width="800"/>
</p>

Use this method after the map has already been created.

Do **not** run SLAM Toolbox when using saved-map navigation with AMCL.

## Terminal 1: Launch Gazebo

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_bringup gazebo.launch.py
```

## Terminal 2: Launch Bridge

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_bringup bridge.launch.py
```

## Terminal 3: Launch Nav2 Saved-Map Navigation

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_nav nav2_slam.launch.py
```

## Terminal 4: Run RViz2

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
rviz2
```

In RViz2:

```text
Fixed Frame: map
```

Use:

```text
2D Pose Estimate
```

to set the initial pose if AMCL does not localize automatically.

Then use:

```text
Nav2 Goal
```

to send a navigation goal.

---

# Depth Control

The project includes depth control for the vertical thrusters.

Run depth controller:

```bash
source ~/unknown_bluerov2_ws/install/setup.bash
ros2 launch unknown_bluerov2_control depth_control.launch.py
```

Example setpoint topic:

```bash
ros2 topic pub /depth/setpoint std_msgs/msg/Float64 "{data: 9.0}" --once
```

Check current depth:

```bash
ros2 topic echo /depth
```

---

# Thruster Mixer

The thruster mixer converts Nav2 `/cmd_vel` commands into BlueROV2 thruster commands.

Typical flow:

```text
Nav2 /cmd_vel_nav -> cmd_vel_thruster_mixer -> Gazebo thrusters
```

Important parameters:

```text
linear_gain
yaw_gain
max_thrust
force_forward_only
block_rotate_in_place
invert_yaw
```

Check Nav2 velocity:

```bash
ros2 topic echo /cmd_vel_nav
```

Check mixer node:

```bash
ros2 node list | grep mixer
```

Manual forward test:

```bash
ros2 topic pub /cmd_vel_nav geometry_msgs/msg/Twist \
"{linear: {x: 0.2}, angular: {z: 0.0}}" -r 10
```

Manual yaw test:

```bash
ros2 topic pub /cmd_vel_nav geometry_msgs/msg/Twist \
"{linear: {x: 0.0}, angular: {z: 0.2}}" -r 10
```

Stop command:

```bash
ros2 topic pub /cmd_vel_nav geometry_msgs/msg/Twist \
"{linear: {x: 0.0}, angular: {z: 0.0}}" --once
```

---

# Check Nav2 Lifecycle

Check if Nav2 nodes are active:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator
```

Expected:

```text
active [3]
```

---

# Check Nav2 TF Tree

Nav2 requires:

```text
map -> odom -> base_link -> laser_link
```

Check `odom -> base_link`:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Check `map -> odom`:

```bash
ros2 run tf2_ros tf2_echo map odom
```

Check `map -> base_link`:

```bash
ros2 run tf2_ros tf2_echo map base_link
```

Notes:

* `map -> odom` is published by SLAM Toolbox during mapping.
* `map -> odom` is published by AMCL during saved-map navigation.
* `odom -> base_link` is published by EKF or odom TF publisher.
* `base_link -> laser_link` is published by static TF.

---

# Check Important ROS 2 Topics

Check map:

```bash
ros2 topic echo /map --once
```

Check AMCL pose:

```bash
ros2 topic echo /amcl_pose --once
```

Check raw odom:

```bash
ros2 topic echo /odom --once
```

Check EKF odom:

```bash
ros2 topic echo /odometry/filtered --once
```

Check lidar:

```bash
ros2 topic echo /scan --once
```

Check Nav2 velocity command:

```bash
ros2 topic echo /cmd_vel_nav
```

Check global plan:

```bash
ros2 topic echo /plan --once
```

Check TF frames:

```bash
ros2 run tf2_tools view_frames
```

---

# Manual Static TF Commands

If sensor TFs are missing, publish them manually.

## `base_link -> laser_link`

```bash
ros2 run tf2_ros static_transform_publisher \
  0.25 0.0 0.0 \
  0.0 0.0 0.0 \
  base_link laser_link
```

## `base_link -> imu_link`

```bash
ros2 run tf2_ros static_transform_publisher \
  0.0 0.0 0.0 \
  0.0 0.0 0.0 \
  base_link imu_link
```

## `base_link -> dvl_link`

```bash
ros2 run tf2_ros static_transform_publisher \
  0.0 0.0 -0.15 \
  0.0 0.0 0.0 \
  base_link dvl_link
```

## `base_link -> depth_link`

```bash
ros2 run tf2_ros static_transform_publisher \
  0.0 0.0 -0.1 \
  0.0 0.0 0.0 \
  base_link depth_link
```

---

# Manual Odom TF Publisher

If EKF does not publish `odom -> base_link`, use:

```bash
ros2 run unknown_bluerov2_nav odom_tf_publisher \
  --ros-args \
  -p use_sim_time:=true \
  -p odom_topic:=/odom \
  -p parent_frame:=odom \
  -p child_frame:=base_link
```

Or use the combined launch:

```bash
ros2 launch unknown_bluerov2_nav tf_with_odom.launch.py
```

Important:

Do not run two nodes publishing the same `odom -> base_link` TF.

Check EKF TF setting:

```bash
ros2 param get /ekf_filter_node publish_tf
```

If EKF publishes TF, do not run `odom_tf_publisher`.

---

# Troubleshooting

## Problem: `odom -> base_link` TF is missing

Check odometry:

```bash
ros2 topic echo /odom --once
```

Check EKF:

```bash
ros2 topic echo /odometry/filtered --once
```

Check TF:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

If missing, run:

```bash
ros2 launch unknown_bluerov2_nav tf_with_odom.launch.py
```

Or enable EKF TF publishing in:

```text
src/unknown_bluerov2_nav/config/ekf_dvl_imu_depth.yaml
```

---

## Problem: `map` frame does not exist

During mapping, SLAM Toolbox must publish `map -> odom`.

Check:

```bash
ros2 node list | grep slam
ros2 run tf2_ros tf2_echo map odom
```

During saved-map navigation, AMCL must publish `map -> odom`.

Check:

```bash
ros2 node list | grep amcl
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map odom
```

---

## Problem: Nav2 says robot is out of costmap bounds

Check:

```bash
ros2 run tf2_ros tf2_echo map base_link
ros2 run tf2_ros tf2_echo odom base_link
```

Clear costmaps:

```bash
ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}"
ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}"
```

Make sure initial pose is correct in RViz2.

---

## Problem: BlueROV2 does not move

Check Nav2 command:

```bash
ros2 topic echo /cmd_vel_nav
```

If `/cmd_vel_nav` publishes velocity but the robot does not move, check the thruster mixer.

Check mixer:

```bash
ros2 node list | grep mixer
ros2 node info /cmd_vel_thruster_mixer
```

Manual command test:

```bash
ros2 topic pub /cmd_vel_nav geometry_msgs/msg/Twist \
"{linear: {x: 0.2}, angular: {z: 0.0}}" -r 10
```

If the robot still does not move, check thruster bridge topics.

---

## Problem: BlueROV2 moves backward during normal path following

Normal path following should be forward-only.

In `nav2_params.yaml`, use:

```yaml
FollowPath:
  min_vel_x: 0.0
```

Keep the mixer able to reverse only if you want Nav2 recovery backup:

```python
"force_forward_only": False
```

This means:

```text
Normal DWB FollowPath = forward only
Nav2 BackUp recovery = can move backward when stuck
```

---

## Problem: Path is opposite of BlueROV2 and robot does not align

Use small reverse motion only if needed:

```yaml
FollowPath:
  min_vel_x: -0.025
```

Add `PreferForward` critic to discourage reverse during normal driving:

```yaml
critics: [
  "RotateToGoal",
  "Oscillation",
  "BaseObstacle",
  "PreferForward",
  "GoalAlign",
  "PathAlign",
  "PathDist",
  "GoalDist"
]

PreferForward.scale: 5.0
```

If the robot moves backward too often, increase:

```yaml
PreferForward.scale: 8.0
```

---

## Problem: BlueROV2 gets stuck near obstacle

Use moderate costmap inflation for narrow paths:

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      robot_radius: 0.34
      inflation_layer:
        inflation_radius: 0.55
        cost_scaling_factor: 4.0
```

Use stronger inflation for safer navigation:

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      robot_radius: 0.50
      inflation_layer:
        inflation_radius: 1.05
        cost_scaling_factor: 2.0
```

If the map contains a V-shaped trap or narrow corner, edit the map or use a keepout zone.

---

## Problem: AMCL shows too many arrows in RViz2

Reduce particles in `nav2_params.yaml`:

```yaml
amcl:
  ros__parameters:
    min_particles: 120
    max_particles: 500
```

Or hide the AMCL particle display in RViz2.

---

## Problem: Gazebo or RViz2 is lagging

Close heavy RViz2 displays.

Reduce costmap update rates:

```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
```

Use fewer AMCL particles:

```yaml
amcl:
  ros__parameters:
    min_particles: 100
    max_particles: 400
```

---

## Author

Kasiphat Uppaphak
GitHub: [wattanatum](https://github.com/wattanatum)

