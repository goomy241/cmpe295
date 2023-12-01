#!/usr/bin/env python3
import os
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from custom_interfaces.msg import InferenceResult
from custom_interfaces.msg import Yolov8Inference
import logging
import time
import torch

bridge = CvBridge()
class Yolov8_publisher(Node):
    def __init__(self):
        super().__init__('Yolov8_publisher')
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.declare_parameter('model_path', current_dir + '/yolov8n.pt')
        self.model_path = self.get_parameter('model_path').value
        self.model = YOLO(self.model_path)
        self.yolov8_inference = Yolov8Inference()

        self.subscription = self.create_subscription(
            Image,
            '/kitti/left_camera/image',
            self.camera_callback,
            10)
        self.subscription 
  
        self.yolov8_pub = self.create_publisher(Yolov8Inference, "/yolov8/inference", 10)
        self.img_pub = self.create_publisher(Image, "/yolov8/result", 10)

    def camera_callback(self, data):

        # Log the latency
        receive_time = time.monotonic()
        logging.getLogger('yolo_infer').info("image receive time: {:.6f} s".format(receive_time))

        img = bridge.imgmsg_to_cv2(data, "8UC3")
        results = self.model(img, device=0) # cpu=cpu, gpu=0 

        infer_time = time.monotonic()
        logging.getLogger('yolo_infer').info("image infer time: {:.6f} s".format(infer_time))

        self.yolov8_inference.header.frame_id = "base_link"
  
        self.yolov8_inference.header.stamp = self.get_clock().now().to_msg()
        # self.yolov8_inference.header = data.header
        for r in results:
            boxes = r.boxes
            for box in boxes:
                self.inference_result = InferenceResult()
                b = box.xyxy[0].to('cpu').detach().numpy().copy()  # get box coordinates in (top, left, bottom, right) format
                c = box.cls
                self.inference_result.class_name = self.model.names[int(c)]
                self.inference_result.top = int(b[0])
                self.inference_result.left = int(b[1])
                self.inference_result.bottom = int(b[2])
                self.inference_result.right = int(b[3])
                self.yolov8_inference.yolov8_inference.append(self.inference_result)
            #camera_subscriber.get_logger().info(f"{self.yolov8_inference}")
        annotated_frame = results[0].plot()
        img_msg = bridge.cv2_to_imgmsg(annotated_frame)
        img_msg.header = data.header
        self.img_pub.publish(img_msg)
        self.yolov8_pub.publish(self.yolov8_inference)

        box_time = time.monotonic()
        logging.getLogger('yolo_infer').info("bounding box time: {:.6f} s".format(box_time))

        self.yolov8_inference.yolov8_inference.clear()

def main(args=None):
    # create logger
    logger = logging.getLogger('yolo_infer')
    logger.setLevel(logging.INFO)
    log_dir =  os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, 'yolo_infer_1000_10.log')
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('=====================This is the log for Yolov8_publisher node.')

    rclpy.init(args=None)
    yolov8_publisher = Yolov8_publisher()
    rclpy.spin(yolov8_publisher)
    rclpy.shutdown()
if __name__ == '__main__':
    main()