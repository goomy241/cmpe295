#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import os

from sensor_msgs.msg import Image
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header

import cv2
from cv_bridge import CvBridge
import numpy as np

import time


class KittiPublisher(Node):
    def __init__(self):
        super().__init__('kitti_publisher')
        self.publisher_ = self.create_publisher(Image, 'kitti_image', 10)
        self.pointcloud_publisher_ = self.create_publisher(PointCloud2, 'kitti_pointcloud', 10)

        # load kitti data
        self.kitti_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..', 'dataset', 'kitti', '2011_09_26', '2011_09_26_drive_0001_sync')
        self.image_files = os.path.join(self.kitti_dir, 'image_02', 'data')
        self.velodyne_files = os.path.join(self.kitti_dir, 'velodyne_points', 'data')

        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.seq = 0
        self.total_images = len(os.listdir(self.image_files))
        self.bridge = CvBridge()
        # self.last_publish_time = time.monotonic()

    def timer_callback(self):
        velodyne_file = os.path.join(self.velodyne_files, '{:010d}.bin'.format(self.seq))
        image_file = os.path.join(self.image_files, '{:010d}.png'.format(self.seq))

        # publish image
        image = cv2.imread(image_file)
        image_msg = self.bridge.cv2_to_imgmsg(image, encoding='bgr8')
        image_msg.header = Header()
        image_msg.header.stamp = self.get_clock().now().to_msg()
        image_msg.header.frame_id = 'kitti'
        self.publisher_.publish(image_msg)

        # publish pointcloud
        with open(velodyne_file, 'rb') as f:
            velodyne = np.fromfile(f, dtype=np.float32).reshape(-1, 4)
            pointcloud = np.zeros((velodyne.shape[0], 4), dtype=np.float32)
            pointcloud[:, 0] = velodyne[:, 0]
            pointcloud[:, 1] = velodyne[:, 1]
            pointcloud[:, 2] = velodyne[:, 2]
            intensity = pointcloud[:, 3]

        pointcloud_msg = PointCloud2()
        pointcloud_msg.header = Header()
        pointcloud_msg.header.stamp = self.get_clock().now().to_msg()
        pointcloud_msg.header.frame_id = 'kitti_velodyne'

        # specify pointcloud data
        pointcloud_msg.height = 1
        pointcloud_msg.width = pointcloud.shape[0]
        pointcloud_msg.fields.append(PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1))
        pointcloud_msg.fields.append(PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1))
        pointcloud_msg.fields.append(PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1))
        pointcloud_msg.fields.append(PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1))
        pointcloud_msg.is_bigendian = False
        pointcloud_msg.point_step = 16
        pointcloud_msg.row_step = pointcloud_msg.point_step * pointcloud_msg.width
        pointcloud_msg.is_dense = True
        pointcloud_msg.data = pointcloud.tobytes() + intensity.tobytes()
        self.pointcloud_publisher_.publish(pointcloud_msg)

        # Log the latency
        # current_time = time.monotonic()
        # latency = current_time - self.last_publish_time
        # logging.getLogger('kitti_publisher').info(f'Latency: {latency:.3f} seconds')
        # self.last_publish_time = current_time
        self.get_logger().info('Publishing image: %s' % image_file)
        self.get_logger().info('Publishing pointcloud: %s' % velodyne_file)

        self.seq += 1
        if self.seq >= self.total_images:
            self.get_logger().info('All images have been published. Exiting node.')
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    kitti_publisher = KittiPublisher()
    rclpy.spin(kitti_publisher)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
