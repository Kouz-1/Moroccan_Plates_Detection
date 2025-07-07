import time
import os
import cv2
from predict_crop import crop_license_plate
from main_char import process_plate

def process_image(image_path):
    """Process a single image: Detect license plate, crop, and extract OCR."""
    # Step 1: Crop license plate using YOLOv5
    cropped_image_path = crop_license_plate(image_path)
    print(f"Cropped image saved at {cropped_image_path}")
    
    # Pass cropped plate to character segmentation (main_char.py will automatically handle this)
    process_plate(cropped_image_path)

def process_video(video_path):
    """Process a video, extracting frames for license plate detection and OCR."""
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Save the current frame as an image to process
        image_path = f"temp_frame_{int(time.time())}.jpg"
        cv2.imwrite(image_path, frame)
        
        # Process the image
        process_image(image_path)

        # Wait for a short period before processing the next frame
        time.sleep(1)
    
    cap.release()

def process_live_feed():
    """Process a live camera feed for license plate detection and OCR every 1 second."""
    cap = cv2.VideoCapture(0)  # 0 is the default camera
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    last_capture_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        if current_time - last_capture_time >= 1.0:
            last_capture_time = current_time

            timestamp = int(current_time)
            image_path = f"temp_frame_live_{timestamp}.jpg"
            cv2.imwrite(image_path, frame)

            process_image(image_path)

if __name__ == "__main__":
    # Choose the mode: Image, Video, or Live Camera Feed
    mode = input("Select mode (image/video/live): ").lower()

    if mode == 'image':
        image_path = input("Enter the image path: ")
        process_image(image_path)

    elif mode == 'video':
        video_path = input("Enter the video path: ")
        process_video(video_path)

    elif mode == 'live':
        process_live_feed()

    else:
        print("Invalid mode selected.")

