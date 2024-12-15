from obswebsocket import obsws, requests, exceptions

# Connection details
host = "localhost"
port = 4444  # Default WebSocket port
password = "your_password"  # Change if you set a password

try:
    # Connect to OBS WebSocket
    print("Connecting to OBS WebSocket...")
    ws = obsws(host, port, password)
    ws.connect()
    print("Connected to OBS WebSocket!")

    # Example: Switch to a specific scene
    scene_name = "Scene Name"  # Replace with the name of a scene in OBS
    print(f"Switching to scene: {scene_name}")
    ws.call(requests.SetCurrentScene(scene_name=scene_name))
    print(f"Successfully switched to scene: {scene_name}")

    # Example: Start Streaming
    print("Starting streaming...")
    ws.call(requests.StartStreaming())
    print("Streaming started successfully!")

    # Example: Stop Streaming
    print("Stopping streaming...")
    ws.call(requests.StopStreaming())
    print("Streaming stopped successfully!")

except exceptions.ConnectionFailure:
    print("Failed to connect to OBS WebSocket. Check if OBS WebSocket server is running.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Disconnect
    try:
        ws.disconnect()
        print("Disconnected from OBS WebSocket.")
    except:
        pass
