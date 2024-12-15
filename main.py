import cv2
import time
from ultralytics import YOLO

def detect_cameras():
    """
    Detect available cameras and return the indices of all cameras.
    OBS Virtual Camera is prioritized if found.
    Returns:
        - A dictionary of available cameras with their index and name.
        - The default OBS Virtual Camera index if detected.
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

def main():
    # Detect all cameras and prioritize OBS Virtual Camera
    cameras, obs_index = detect_cameras()

    # Display detected cameras and let the user choose
    default_camera_index = obs_index if obs_index is not None else next(iter(cameras.keys()))
    print(f"\nDefault camera: {cameras[default_camera_index]} (Index: {default_camera_index})")

    user_input = input(f"Enter the camera index to use (default is {default_camera_index}): ")
    camera_index = int(user_input) if user_input.isdigit() and int(user_input) in cameras else default_camera_index
    print(f"\nUsing camera: {cameras[camera_index]} (Index: {camera_index})\n")

    # Initialize YOLOv8 model (pre-trained weights)
    model = YOLO("yolov8n.pt")  # Use yolov8n.pt or custom weights

    # Access the selected camera
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Cannot access the selected camera. Check if it's running.")
        exit()

    # Optionally set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Initialize FPS calculation
    prev_time = time.time()

    print("Starting object detection on the selected camera feed...")
    window_name = "Object Detection"

    # Set up the display window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 360)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture frame.")
            break

        # Perform YOLO object detection
        results = model(frame)

        # Annotate the frame with bounding boxes and labels
        annotated_frame = results[0].plot()

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

        # Display detection count
        detection_count = len(results[0].boxes) if results[0].boxes else 0
        cv2.putText(
            annotated_frame,
            f"Objects Detected: {detection_count}",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
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
