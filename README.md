# cmpe295

## Prerequisites

- ros2-humble, kitti, opencv, pcl

1. Install ROS2 Humble
follow the instructions [here](https://docs.ros.org/en/humble/Installation.html)

2. install tools and dependencies
```bash
sudo apt install python3-colcon-common-extensions python3-opencv ros-humble-pcl python3-colcon-common-extensions
```

3. download kitti dataset (optional)

4. Compile the project
```bash
colcon build --cmake-clean-cache
```

5. Run the project
```bash
ros2 launch cmpe295_bringup display.launch.xml
```