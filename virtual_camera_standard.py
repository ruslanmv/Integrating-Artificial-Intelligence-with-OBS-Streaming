import cv2

def find_camera_index():
    """
    Tries to find the correct camera index by iterating through indices.
    """
    for index in range(10):  # Test the first 10 camera indices
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # CAP_DSHOW improves compatibility on Windows
        if cap.isOpened():
            print(f"Camera found at index: {index}")
            cap.release()
            return index
    print("No camera detected. Ensure OBS Virtual Camera is enabled.")
    return -1

# Find the correct camera index
camera_index = find_camera_index()
if camera_index == -1:
    exit(1)  # Exit if no camera is found

# Access OBS Virtual Camera or default webcam
cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # CAP_DSHOW for better compatibility on Windows

# Set a small window size
window_name = "OBS Stream"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 640, 360)  # Adjust window size to make it smaller

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame. Check your OBS Virtual Camera or webcam settings.")
        break

    # Overlay text on the frame
    cv2.putText(frame, "Live Streaming!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Display the captured frame
    cv2.imshow(window_name, frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
