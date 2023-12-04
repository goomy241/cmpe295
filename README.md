# cmpe295

## Prerequisites

- ros2-humble, opencv, pcl, OpenPCDet

1. Install ROS2 Humble
follow the instructions [here](https://docs.ros.org/en/humble/Installation.html)

2. Install tools and dependencies
```bash
sudo apt install python3-colcon-common-extensions python3-opencv ros-humble-pcl python3-colcon-common-extensions ros-humble-vision_msgs
pip3 install ultralytics
pip3 install mmdet3d
```
3. Install gpu libraries if you want to run on gpu, you can follow [here](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#ubuntu-installation) to install cuda and cudnn. Here I am using cuda 11.7 and cudnn 8.9.0.

4. Ensure OpenPCDet is installed successfully and demo runs as expected
- [Installation Guide](https://github.com/open-mmlab/OpenPCDet/blob/master/docs/INSTALL.md)
- [Demo Guide](https://github.com/open-mmlab/OpenPCDet/blob/master/docs/DEMO.md) 

6. Compile the project
```bash
colcon build --cmake-clean-cache
```

6. Run the project
- Dataset Preparation:
  - Download the nuScenes dataset from [here](https://www.nuscenes.org/nuscenes#download)
  - Doanload the kitti dataset from [here](https://www.cvlibs.net/datasets/kitti/raw_data.php)
  - Doanload the pretrained model from [here](https://github.com/open-mmlab/OpenPCDet#model-zoo) and put it under `cmpe295/src/pcdet_ros2/checkpoints/` folder
  - Change the path in launch file under `cmpe295/src/ros2_dataset_bridge/launch` folder accordingly 

- Start the project
  - To Publish from nuScenes dataset
  ```bash
  # publish nuscenes:
  ros2 launch ros2_dataset_bridge nuscenes_launch.xml
  
  # start rviz2:
  ros2 launch cmpe295_bringup display.launch.xml
  
  # start pcdet
  ros2 launch pcdet_ros2 pp_multihead_nds.launch.xml
  
  # uncheck "stop" option in the control panel
  ```

  - To Publish from kitti dataset
    - Switch to 'kitti-infer' branch and build the project
  ```bash
  # publish kitti:
  ros2 launch ros2_dataset_bridge kitti_launch.xml
  
  # start rviz2:
  ros2 launch cmpe295_bringup display.launch.xml
  
  # start pcdet
  ros2 launch pcdet_ros2 pointpillar.launch.xml
  
  # uncheck "stop" option in the control panel
  ```
