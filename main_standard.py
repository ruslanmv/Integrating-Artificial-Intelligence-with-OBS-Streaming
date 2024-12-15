import cv2
import time
from ultralytics import YOLO

def detect_cameras():
    """
    Detect available cameras and return the index of OBS Virtual Camera.
    """
    obs_index = None
    available_cameras = {}

    print("Detecting available cameras...\n")
    for index in range(10):  # Test camera indices 0 to 9
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                camera_name = f"Camera Index {index}"
                if index == 1:  # OBS Virtual Camera is often index 1
                    camera_name = "OBS Virtual Camera (Default)"
                    obs_index = index

                available_cameras[index] = camera_name
                print(f"[{index}] {camera_name}")
            cap.release()

    if not available_cameras:
        print("No cameras detected. Ensure OBS Virtual Camera or webcam is enabled.")
        exit(1)

    return obs_index if obs_index is not None else 0  # Default to 0 if OBS not found

def main():
    # Detect the OBS Virtual Camera index
    camera_index = detect_cameras()
    print(f"\nUsing camera index: {camera_index}\n")

    # Initialize YOLOv8 model (pre-trained weights)
    model = YOLO("yolov8n.pt")  # Use yolov8n.pt or custom weights

    # Access the selected camera
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Cannot access the selected camera. Check if it's running.")
        exit()

    # Set resolution (optional)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Initialize FPS calculation
    prev_time = time.time()
    fps = 0

    print("Starting object detection on OBS Virtual Camera feed...")

    while True:
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read from OBS Virtual Camera.")
            break

        # Perform YOLO object detection
        results = model(frame)

        # Annotate frame with bounding boxes and labels
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

        # Display additional detection information
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

        # Display the annotated frame
        cv2.imshow("OBS Object Detection", annotated_frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
