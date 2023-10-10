import message_filters
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2, Imu, NavSatFix
from vision_msgs.msg import Detection3DArray
from visualization_msgs.msg import MarkerArray


class DetectionVisualizerNode(Node):

    def __init__(self):
        super().__init__('detection_visualizer')

        # point cloud
        self._pc_sub = message_filters.Subscriber(self, PointCloud2, '/kitti/point_cloud')
        self._pc_pub = self.create_publisher(PointCloud2, '/synchronized/kitti/point_cloud', 10)

        # gray image left
        self._g_image01_sub = message_filters.Subscriber(self, Image, '/kitti/image/gray/left')
        self._g_image01_pub = self.create_publisher(Image, '/synchronized/kitti/image/gray/left', 10)

        # gray image right
        self._g_image02_sub = message_filters.Subscriber(self, Image, '/kitti/image/gray/right')
        self._g_image02_pub = self.create_publisher(Image, '/synchronized/kitti/image/gray/right', 10)

        # color image left
        self._c_image01_sub = message_filters.Subscriber(self, Image, 'kitti/image/color/left')
        self._c_image01_pub = self.create_publisher(Image, '/synchronized/kitti/image/color/left', 10)

        # color image right
        self._c_image02_sub = message_filters.Subscriber(self, Image, '/kitti/image/color/right')
        self._c_image02_pub = self.create_publisher(Image, '/synchronized/kitti/image/color/right', 10)

        # imu
        self._imu_sub = message_filters.Subscriber(self, Imu, '/kitti/imu')
        self._imu_pub = self.create_publisher(Imu, '/synchronized/kitti/imu', 10)

        # gps
        self._gps_sub = message_filters.Subscriber(self, NavSatFix, '/kitti/nav_sat_fix')
        self._gps_pub = self.create_publisher(NavSatFix, '/synchronized/kitti/nav_sat_fix', 10)

        # marker array
        self._marker_sub = message_filters.Subscriber(self, MarkerArray, '/kitti/marker_array')
        self._marker_pub = self.create_publisher(MarkerArray, '/synchronized/kitti/marker_array', 10)

        # yolov8 result
        self._yolov8_result_sub = message_filters.Subscriber(self, Image, '/yolov8/result')
        self._yolov8_result_pub = self.create_publisher(Image, '/synchronized/yolov8/result', 10)

        # pointpillars result
        self.openpcdet_result_sub = message_filters.Subscriber(self, Detection3DArray, '/openpcdet/result')
        self.openpcdet_result_pub = self.create_publisher(Detection3DArray, '/synchronized/openpcdet/result', 10)

        self._sub_arr = [
                         self._pc_sub, 
                         self._g_image01_sub, 
                         self._g_image02_sub, 
                         self._c_image01_sub, 
                         self._c_image02_sub, 
                         self._imu_sub, 
                         self._gps_sub,
                        #  self._marker_sub, # no header in marker array
                         self._yolov8_result_sub, 
                         self.openpcdet_result_sub
                         ]
        self._ts = message_filters.ApproximateTimeSynchronizer(self._sub_arr, 10, 1, allow_headerless=True)
        self._ts.registerCallback(self.on_detections)
    

    def on_detections(self, pc, g_image01, g_image02, c_image01, c_image02, imu, gps, yolov8_result, openpcdet_result):
        self._pc_pub.publish(pc)
        self._g_image01_pub.publish(g_image01)
        self._g_image02_pub.publish(g_image02)
        self._c_image01_pub.publish(c_image01)
        self._c_image02_pub.publish(c_image02)
        self._imu_pub.publish(imu)
        self._gps_pub.publish(gps)
        # self._marker_pub.publish(marker)
        self._yolov8_result_pub.publish(yolov8_result)
        self.openpcdet_result_pub.publish(openpcdet_result)
        


def main():
    rclpy.init()
    detection_visualizer = DetectionVisualizerNode()
    rclpy.spin(detection_visualizer)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
