"""
mouse_detection_node.py

This module creates the mouse_detection_node which is responsible for collecting
sensor data (camera images) from sensor_fusion_pkg and running motion detection,
on specified object, providing action trigger for rc_navigation_pkg.

The node defines:
    image_subscriber: A subscriber to the /sensor_fusion_pkg/sensor_msg published
                      by the sensor_fusion_pkg with sensor data.
    display_image_publisher: A publisher to publish the Image message using
                             web_video_server.
    mouse_publisher: A publisher to publish whether a mouse was detected or not.
"""

import time
import signal
import threading
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import (QoSProfile,
                       QoSHistoryPolicy,
                       QoSReliabilityPolicy)
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

from deepracer_interfaces_pkg.msg import (EvoSensorMsg,
                                          DetectionDeltaMsg)
from mouse_detection_pkg import utils

class MouseDetectionNode(Node):
    """Node responsible for collecting sensor data (camera images) from sensor_fusion_pkg
       and running motion detection on mouse object, providing action_trigger for rc_navigation_pkg.
    """

    def __init__(self, qos_profile):
        """Create a MouseDetectionNode.
        """
        super().__init__('mouse_detection_node')
        self.get_logger().info("mouse_detection_node started.")

        # Initialize variables
        self.previous_sensor_data = None
        self.h = 160
        self.w = 120

        # Double buffer to hold the input images for inference.
        self.input_buffer = utils.DoubleBuffer(clear_data_on_get=True)
        # Get DEVICE parameter (CPU/MYRIAD) from launch file.
        self.declare_parameter("DEVICE")
        self.device = self.get_parameter("DEVICE").get_parameter_value().string_value
        if not self.device:
            self.device = constants.DEVICE

        # Create subscription to sensor messages from camera.
        self.image_subscriber = self.create_subscription(EvoSensorMsg,
                                                         constants.SENSOR_FUSION_TOPIC,
                                                         self.on_image_received_cb,
                                                         qos_profile)

        # Creating publisher for confidence score of mouse detection.
        self.delta_publisher = self.create_publisher(MouseDetectionConfidence,
                                                     constants.MOUSE_PUBLISHER_TOPIC,
                                                     qos_profile)
        self.bridge = CvBridge()

        # Launching a separate thread to run inference.
        self.stop_thread = False
        self.thread_initialized = False
        self.thread = threading.Thread(target=self.run_inference)
        self.thread.start()
        self.thread_initialized = True
        self.get_logger().info(f"Waiting for input images on {constants.SENSOR_FUSION_TOPIC}")

    def wait_for_thread(self):
        """Function which joins the created background thread.
        """
        if self.thread_initialized:
            self.thread.join()
            self.get_logger().info("Thread joined")

    def thread_shutdown(self):
        """Function which sets the flag to shutdown background thread.
        """
        self.stop_thread = True

    def on_image_received_cb(self, sensor_data):
        """Call back for adding to the input double buffer whenever
           new sensor image is received from sensor_fusion_node.
        Args:
            sensor_data (EvoSensorMsg): Message containing sensor images and lidar data.
        """
        self.input_buffer.put(sensor_data)
    
    def preprocess(self, sensor_data):
        """Method that preprocesses the input data to be provided for inference to network.
        Args:
            sensor_data (EvoSensorMsg): Contains sensor images and lidar data.
        Returns:
            image: Preprosessed image expected by the network.
        """
        image = self.bridge.imgmsg_to_cv2(sensor_data.images[0])
        ih, iw = image.shape[:-1]
        self.get_logger().info("Height and width of images")
        self.get_logger().info(ih)
        self.get_logger().info(iw)
        # Resize to required input size
        if (ih, iw) != (int(self.h), int(self.w)):
            image = cv2.resize(image, (int(self.w), int(self.h)))
        # Change data layout from HWC to CHW.
        image = image.transpose((2, 0, 1))
        return image

    def run_inference(self):
        """Method for running inference on received input image.
        """

        try:
            while not self.stop_thread:
                
                # Get an input image from double buffer.
                sensor_data = self.input_buffer.get()
                start_time = time.time()

                # Pre-process input.
                input_data = {}
                input_data['current_sensor_data'] = self.preprocess(sensor_data)
                data_type = str(type(input_data['current_sensor_data']))
                self.get_logger().info(f"Type of output from self.preprocess - {data_type}")
                
                # Initialize previous image
                if previous_sensor_data == None:
                    previous_sensor_data = input['current_sensor_data']
                else:
                    input['previous_sensor_data'] = self.previous_sensor_data
                    self.previous_sensor_data = input['current_sensor_data']

                # Assume being at target position.
                detection_delta = cv2.absdiff(input['previous_sensor_data'], input['current_sensor_data'])
                self.get_logger().info(f"detection_delta is: {detection_delta}")
                self.delta_publisher.publish(detection_delta)

                self.get_logger().info(f"Total execution time = {time.time() - start_time}")
        except Exception as ex:
            self.get_logger().error(f"Failed inference step: {ex}")
            # Destroy the ROS Node running in another thread as well.
            self.destroy_node()
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    qos = QoSProfile(reliability=QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT,
                     depth=1,
                     history=QoSHistoryPolicy.RMW_QOS_POLICY_HISTORY_KEEP_LAST)

    try:
        mouse_detection_node = MouseDetectionNode(qos)
        executor = MultiThreadedExecutor()

        def signal_handler(signum, frame):
            """Callback function to handle registered signal handler
               to join and stop executing running thread created.
            Args:
                signum: The signal number
                frame: the current stack frame (None or a frame object)
            """
            mouse_detection_node.get_logger().info("Signal Handler initiated")
            mouse_detection_node.thread_shutdown()
            mouse_detection_node.wait_for_thread()

        # Register SIGINT handler
        signal.signal(signal.SIGINT, signal_handler)

        rclpy.spin(mouse_detection_node, executor)

    except Exception as ex:
        mouse_detection_node.get_logger().error(f"Exception in Mouse Detection Node: {ex}")
        mouse_detection_node.destroy_node()
        rclpy.shutdown()

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    mouse_detection_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
