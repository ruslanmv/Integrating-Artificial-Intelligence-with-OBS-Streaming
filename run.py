import cv2
import time
import threading
from ultralytics import YOLO
import speech_recognition as sr

# Global variable for subtitles
subtitle_text = ""

def detect_cameras():
    """
    Detect available cameras and return the indices of all cameras.
    OBS Virtual Camera is prioritized if found.
    """
    available_cameras = {}
    obs_index = None

    print("Detecting available cameras...\n")
    for index in range(10):  # Test camera indices 0 to 9
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                # Name OBS Virtual Camera as default if detected
                camera_name = f"Camera Index {index}"
                if index == 1:  # OBS Virtual Camera is typically at index 1
                    camera_name = "OBS Virtual Camera (Default)"
                    obs_index = index

                available_cameras[index] = camera_name
                print(f"[{index}] {camera_name}")
            cap.release()

    if not available_cameras:
        print("No cameras detected. Ensure OBS Virtual Camera or webcam is enabled.")
        exit(1)

    return available_cameras, obs_index

def speech_to_text():
    """
    Runs speech recognition in a separate thread to avoid blocking video capture.
    Updates the global variable 'subtitle_text' with recognized speech.
    """
    global subtitle_text
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Initializing microphone for speech recognition...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)  # Calibrate for background noise

    while True:
        try:
            with microphone as source:
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)
                subtitle_text = recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            subtitle_text = ""  # No audio detected
        except sr.UnknownValueError:
            subtitle_text = ""  # Could not understand audio
        except Exception as e:
            print(f"Speech recognition error: {e}")
            subtitle_text = ""

def main():
    global subtitle_text

    # Detect all cameras and prioritize OBS Virtual Camera
    cameras, obs_index = detect_cameras()

    # Display detected cameras and let the user choose
    default_camera_index = obs_index if obs_index is not None else next(iter(cameras.keys()))
    print(f"\nDefault camera: {cameras[default_camera_index]} (Index: {default_camera_index})")

    user_input = input(f"Enter the camera index to use (default is {default_camera_index}): ")
    camera_index = int(user_input) if user_input.isdigit() and int(user_input) in cameras else default_camera_index
    print(f"\nUsing camera: {cameras[camera_index]} (Index: {camera_index})\n")

    # Ask user if they want to enable object detection
    use_object_detection = input("Do you want to enable object detection? (y/n): ").strip().lower()
    if use_object_detection == 'y':
        print("\nObject detection enabled. Initializing YOLOv8...")
        model = YOLO("yolov8n.pt")  # Initialize YOLO model
    else:
        print("\nObject detection disabled. Displaying subtitles only.")
        model = None

    # Access the selected camera
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Cannot access the selected camera. Check if it's running.")
        exit()

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Start the speech recognition thread
    subtitle_thread = threading.Thread(target=speech_to_text, daemon=True)
    subtitle_thread.start()

    # Initialize FPS calculation
    prev_time = time.time()

    print("\nStarting video stream with speech-to-text subtitles...")
    window_name = "Video Stream with Subtitles"

    # Set up the display window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 360)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture frame.")
            break

        # Perform object detection if enabled
        if model:
            results = model(frame)
            annotated_frame = results[0].plot()  # Annotate the frame
        else:
            annotated_frame = frame.copy()  # No annotations, display raw frame

        # Calculate FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # Display FPS on the frame
        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.2f}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        # Display real-time subtitles
        if subtitle_text:
            cv2.putText(
                annotated_frame,
                f"Subtitle: {subtitle_text}",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
            )

        # Show the video feed
        cv2.imshow(window_name, annotated_frame)

        # Exit the loop on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
