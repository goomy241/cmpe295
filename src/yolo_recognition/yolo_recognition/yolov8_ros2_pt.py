#!/usr/bin/env python3

import os
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from custom_interfaces.msg import InferenceResult
from custom_interfaces.msg import Yolov8Inference

import torch

bridge = CvBridge()

class Yolov8_publisher(Node):

    def __init__(self):
        super().__init__('Yolov8_publisher')

        current_dir = os.path.dirname(os.path.realpath(__file__))

        self.declare_parameter('model_path', current_dir + '/yolov8n.pt')
        self.model_path = self.get_parameter('model_path').value
        self.model = YOLO(self.model_path)

        self.channels = ['CAM_BACK', 'CAM_FRONT', 'CAM_FRONT_LEFT', 'CAM_FRONT_RIGHT', 'CAM_BACK_RIGHT', 'CAM_BACK_LEFT']
        self.yolov8_publishers = {}  # Dictionary to store publishers for each camera

        for channel in self.channels:
            self.create_subscription(
                Image,
                f'/nuscenes/{channel}/image',
                lambda data, channel=channel: self.camera_callback(data, channel),
                10)

            # Create publishers for each camera
            inference_topic = f'/yolov8/inference/{channel}'
            self.yolov8_publishers[channel] = self.create_publisher(Yolov8Inference, inference_topic, 10)

    def camera_callback(self, data, channel):

        img = bridge.imgmsg_to_cv2(data, "8UC3")
        results = self.model(img, device=0) # cpu=cpu, gpu=0 

        yolov8_inference = Yolov8Inference()
        yolov8_inference.header.frame_id = f"base_link_{channel}"
        yolov8_inference.header.stamp = self.get_clock().now().to_msg()
        # self.yolov8_inference.header = data.header


        for r in results:
            boxes = r.boxes
            for box in boxes:
                inference_result = InferenceResult()
                b = box.xyxy[0].to('cpu').detach().numpy().copy()  # get box coordinates in (top, left, bottom, right) format
                c = box.cls
                inference_result.class_name = self.model.names[int(c)]
                inference_result.top = int(b[0])
                inference_result.left = int(b[1])
                inference_result.bottom = int(b[2])
                inference_result.right = int(b[3])
                yolov8_inference.yolov8_inference.append(inference_result)

            #camera_subscriber.get_logger().info(f"{self.yolov8_inference}")

        # Publish inference results directly without using the inference_topic variable
        self.yolov8_publishers[channel].publish(yolov8_inference)

        # Optionally, you can also publish the annotated image
        img_msg = bridge.cv2_to_imgmsg(results[0].plot())
        img_msg.header = data.header
        self.create_publisher(Image, f'/yolov8/result/{channel}', 10).publish(img_msg)

def main(args=None):
    rclpy.init(args=None)
    yolov8_publisher = Yolov8_publisher()
    rclpy.spin(yolov8_publisher)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
