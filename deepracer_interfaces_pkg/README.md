# AWS DeepRacer Interfaces Package for RoboCat sample project

## Overview

The DeepRacer Interfaces ROS package is a foundational package that creates the custom service and message types that are used in the core AWS DeepRacer application. The package has been extended and modified to support RoboCat sample project. These services and messages defined are shared across the packages that are part of the AWS DeepRacer application and RoboCat sample project. For more information about the RoboCat sample project, see [RoboCat sample project](https://github.com/msrparadesi/robocat_ws).

## License

The source code is released under [Apache 2.0](https://aws.amazon.com/apache-2-0/).

## Installation

### Prerequisites

The AWS DeepRacer device comes with all the pre-requisite packages and libraries installed to run the RoboCat sample project. More details about pre installed set of packages and libraries on the DeepRacer, and installing required build systems can be found in the [Getting Started](https://github.com/aws-deepracer/aws-deepracer-launcher/blob/main/getting-started.md) section of the AWS DeepRacer Opensource page.

The deepracer_inferfaces_pkg specifically depends on the following ROS2 packages as build and execute dependencies:

1. *rosidl_default_generators* - The custom built interfaces rely on rosidl_default_generators for generating language-specific code.
2. *rosidl_default_runtime* - The custom built interfaces rely on rosidl_default_runtime for using the language-specific code.
3. *sensor_msgs* - This package defines messages for commonly used sensors, including cameras and scanning laser rangefinders.
4. *std_msgs* - Standard ROS Messages including common message types representing primitive data types and other basic message constructs, such as multiarrays.



## Downloading and Building

Open up a terminal on the DeepRacer device and run the following commands as root user.

1. Switch to root user before you source the ROS2 installation:

        sudo su

1. Source the ROS2 Foxy setup script:

        source /opt/ros/foxy/setup.bash

1. Clone the entire RoboCat sample project on the DeepRacer device.

        git clone https://github.com/msrparadesi/robocat_ws.git
        cd ~/robocat_ws/

1. Resolve the dependencies:

        cd ~/robocat_ws/ && rosdep install -i --from-path . --rosdistro foxy -y

1. Build the deepracer_interfaces_pkg:

        cd ~/robocat_ws/ && colcon build --packages-select deepracer_interfaces_pkg

## Resources

* AWS DeepRacer Opensource getting started: [https://github.com/aws-deepracer/aws-deepracer-launcher/blob/main/getting-started.md](https://github.com/aws-deepracer/aws-deepracer-launcher/blob/main/getting-started.md)
* Follow the Leader(FTL) sample project getting started: [https://github.com/aws-deepracer/aws-deepracer-follow-the-leader-sample-project/blob/main/getting-started.md](https://github.com/aws-deepracer/aws-deepracer-follow-the-leader-sample-project/blob/main/getting-started.md)
