import cv2

def detect_cameras():
    """
    Detects all available camera indices and identifies the OBS Virtual Camera.
    Returns:
        - A dictionary of available cameras with their index and name.
        - The default OBS Virtual Camera index if detected.
    """
    available_cameras = {}
    obs_virtual_camera_index = None

    print("Detecting available cameras...\n")
    for index in range(10):  # Test first 10 camera indices
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # Use CAP_DSHOW for Windows compatibility
        if cap.isOpened():
            # Try reading a frame to ensure the camera is functional
            ret, _ = cap.read()
            if ret:
                # Identify OBS Virtual Camera based on index naming or typical order
                camera_name = f"Camera Index {index}"
                if index == 1:  # OBS Virtual Camera often appears at index 1
                    camera_name = "OBS Virtual Camera (Default)"
                    obs_virtual_camera_index = index

                available_cameras[index] = camera_name
                print(f"[{index}] {camera_name}")
            cap.release()

    if not available_cameras:
        print("No cameras detected. Ensure OBS Virtual Camera or webcam is enabled.")
    return available_cameras, obs_virtual_camera_index

def main():
    # Detect cameras and identify OBS Virtual Camera
    cameras, obs_index = detect_cameras()

    if not cameras:
        exit(1)  # Exit if no cameras are found

    # Set the default camera (OBS Virtual Camera or first available)
    default_camera_index = obs_index if obs_index is not None else next(iter(cameras.keys()))
    print(f"\nDefaulting to: {cameras[default_camera_index]} (Index: {default_camera_index})")

    # Allow user to select a camera manually
    user_choice = input(f"Enter camera index to use (default is {default_camera_index}): ")
    camera_index = int(user_choice) if user_choice.isdigit() and int(user_choice) in cameras else default_camera_index

    print(f"Using: {cameras[camera_index]} (Index: {camera_index})\n")

    # Start video capture
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Failed to open the selected camera. Exiting...")
        return

    # Set window properties
    window_name = "OBS Virtual Camera Stream"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 360)  # Set a smaller display window

    print("Press 'q' to quit the video stream.\n")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        # Overlay text on the video feed
        cv2.putText(frame, "Live Streaming!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the video stream
        cv2.imshow(window_name, frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting video stream...")
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
