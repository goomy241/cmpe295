# cmpe295

## Prerequisites

- ros2-humble, kitti, opencv, pcl

1. Install ROS2 Humble
follow the instructions [here](https://docs.ros.org/en/humble/Installation.html)

2. Install tools and dependencies
```bash
sudo apt install python3-colcon-common-extensions python3-opencv ros-humble-pcl python3-colcon-common-extensions ros-humble-vision_msgs
pip3 install ultralytics
```
3. Install gpu libraries if you want to run on gpu, you can follow [here](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#ubuntu-installation) to install cuda and cudnn. Here I am using cuda 11.7 and cudnn 8.9.0.

4. Download kitti dataset (optional)

5. Compile the project
```bash
colcon build --cmake-clean-cache
```

6. Run the project
```bash
ros2 launch cmpe295_bringup display.launch.xml
```