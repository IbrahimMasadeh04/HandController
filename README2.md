# Hand Controller

The Hand Controller is a gesture-based control system that enables users to control their computer's mouse and system volume with hand gestures. By utilizing MediaPipe for hand landmark detection, pyautogui for mouse control, and pycaw for volume control, the project allows users to perform various actions, such as moving the mouse and adjusting volume, using their hands.

## Features

- **Mouse Control**: Control the mouse pointer using hand gestures.
  - Left Click
  - Right Click
  - Double Click
  - Mouse Movement
- **Volume Control**: Adjust system volume using the distance between the thumb and index finger.
- **Multi-hand Support**: Works with up to two hands. The left hand for mouse controlling, and the right hand for volume controlling.
- **Mirror Effect**: Webcam feed is flipped to create a mirror-like experience.

## Installation

Ensure you have Python 3.x installed on your machine. Then, install the required dependencies:

```bash
pip install -r requirements.txt
