#!/usr/bin/env python3

from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from custom_interfaces.msg import InferenceResult
from custom_interfaces.msg import Yolov8Inference

bridge = CvBridge()

class Yolov8_publisher(Node):

    def __init__(self):
        super().__init__('Yolov8_publisher')

        self.model = YOLO('yolov8n.pt')

        self.yolov8_inference = Yolov8Inference()

        self.subscription = self.create_subscription(
            Image,
            'kitti/image/color/left',
            self.camera_callback,
            10)
        self.subscription 

        self.yolov8_pub = self.create_publisher(Yolov8Inference, "/Yolov8_Inference", 1)
        self.img_pub = self.create_publisher(Image, "/inference_result", 1)

    def camera_callback(self, data):

        img = bridge.imgmsg_to_cv2(data, "bgr8")
        results = self.model(img)

        # self.yolov8_inference.header.frame_id = "base_link"
        # self.yolov8_inference.header.stamp = camera_subscriber.get_clock().now().to_msg()
        self.yolov8_inference.header = data.header


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

        self.img_pub.publish(img_msg)
        self.yolov8_pub.publish(self.yolov8_inference)
        self.yolov8_inference.yolov8_inference.clear()

def main(args=None):
    rclpy.init(args=None)
    yolov8_publisher = Yolov8_publisher()
    rclpy.spin(yolov8_publisher)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
