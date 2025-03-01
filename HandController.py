import cv2 as cv
import mediapipe as mp
import pyautogui
import math
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Initialize MediaPipe hands solution for hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Get screen dimensions (width, height)
screen_width, screen_height = pyautogui.size()

# Initialize video capture (webcam)
capture = cv.VideoCapture(0)

"""
0 = default webcam
If webcam index 0 does not work, try index 1 by changing `cv.VideoCapture(0)` to `cv.VideoCapture(1)`.
If it still doesn't work, run the following code to know your camera index:

import cv2 as cv
for i in range(10):
    capture = cv.VideoCapture(i)
    if capture.isOpened():
        print(f"found at idx {i}")
"""

# Initialize the audio interface for controlling system volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Check if webcam opened successfully
if not capture.isOpened():
    raise IOError("Cannot open webcam")

# Initialize the MediaPipe hands model with parameters
with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,  # Support for up to 2 hands
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hand:
    
    while capture.isOpened():

        success, frame = capture.read()

        if not success:
            break

        # Flip the frame horizontally for mirror effect
        frame = cv.flip(frame, 1)

        # Convert the frame to RGB (MediaPipe uses RGB)
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        # Process the frame to detect hand landmarks
        result = hand.process(rgb_frame)

        txt = ''  # Initialize text to display on screen

        if result.multi_hand_landmarks:  # If hands are detected
            
            left_hand = right_hand = None  # Initialize variables for both hands
            
            # Loop through each detected hand
            for idx, landmarks in enumerate(result.multi_hand_landmarks):
                
                # Get hand label (Left or Right)
                hand_label = result.multi_handedness[idx].classification[0].label

                if hand_label == "Left":
                    left_hand = landmarks  # Store left hand landmarks
                else:
                    right_hand = landmarks  # Store right hand landmarks
                
                if left_hand:
                    # Mouse control mode
                    txt = "Mouse Mode"

                    # Get key landmarks for left hand (thumb and index finger)
                    left_thump_tip = left_hand.landmark[4]
                    left_idx_mcp = left_hand.landmark[5]
                    left_idx_tip = left_hand.landmark[8]
                    left_idx_pip = left_hand.landmark[6]
                    left_mdl_pip = left_hand.landmark[10]
                    left_mdl_tip = left_hand.landmark[12]

                    # Convert hand landmarks to screen coordinates
                    idx_tip_x = int(left_idx_tip.x * screen_width)
                    idx_tip_y = int(left_idx_tip.y * screen_height)

                    mdl_tip_y = int(left_mdl_tip.y * screen_height)
                    mdl_pip_y = int(left_mdl_pip.y * screen_height)
                    idx_pip_y = int(left_idx_pip.y * screen_height)

                    if left_thump_tip.y > left_idx_mcp.y:  # Thumb above index means move mouse
                        pyautogui.moveTo(idx_tip_x, idx_tip_y)
                    else:
                        if idx_tip_y > idx_pip_y and mdl_tip_y > mdl_pip_y:
                            pyautogui.doubleClick()  # Double click
                            txt = 'double click'

                        elif idx_tip_y > mdl_pip_y:
                            pyautogui.click()  # Left click
                            txt = 'left click'

                        elif mdl_tip_y > idx_pip_y:
                            pyautogui.rightClick()  # Right click
                            txt = 'right click'
                
                if right_hand:
                    # Get key landmarks for right hand (thumb and index finger)
                    right_thumb_tip = right_hand.landmark[4]
                    right_idx_tip = right_hand.landmark[8]

                    # Convert right hand landmarks to screen coordinates
                    right_thumb_x = int(right_thumb_tip.x * screen_width)
                    right_thumb_y = int(right_thumb_tip.y * screen_height)
                    right_idx_x = int(right_idx_tip.x * screen_width)
                    right_idx_y = int(right_idx_tip.y * screen_height)

                    # Calculate the distance between thumb and index finger
                    distance = math.hypot(right_idx_x - right_thumb_x, right_idx_y - right_thumb_y)
                    
                    # Normalize the distance to be between 0 and 1
                    normalized_distance = min(max(distance / 200, 0), 1)

                    # Display volume percentage
                    txt = f"Volume: {normalized_distance * 100:.2f}%"

                    # Adjust system volume based on normalized distance
                    volume.SetMasterVolumeLevelScalar(normalized_distance, None)
                
                # Draw hand landmarks and connections on the frame
                mp_drawing.draw_landmarks(
                    frame,
                    landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
                )

                # Display the text on the frame
                cv.putText(
                    frame,
                    txt,
                    (10, 30), 
                    cv.FONT_HERSHEY_COMPLEX,
                    1, 
                    (0, 0, 255), 
                    2,
                    cv.LINE_AA
                )
                
        # Display the frame with hand landmarks and text
        cv.imshow("Hand Controller", frame)

        # Exit loop if 'q' is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

# Release the video capture and close all windows
capture.release()
cv.destroyAllWindows()
