import pathlib
pathlib.PosixPath = pathlib.WindowsPath

import cv2
import time
import torch
from pathlib import Path
from PIL import Image
import math
import numpy as np
import matplotlib.pyplot as plt

# Load YOLOv5 model (make sure to change to your model path if needed)
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5_model/best.pt')  # Custom weights

# Directory to save cropped images
output_dir = Path('./cropped_plates')
output_dir.mkdir(parents=True, exist_ok=True)

def rotate_plate(ROI, left_x, left_y, right_x, right_y):
    """
    Rotates the cropped license plate to align it properly.
    
    Parameters:
    - ROI: The region of interest (cropped plate image).
    - left_x, left_y: Coordinates of the left edge of the license plate.
    - right_x, right_y: Coordinates of the right edge of the license plate.
    
    Returns:
    - Rotated image.
    """
    # Step 1: Calculate the angle to rotate
    opp = right_y - left_y
    hyp = math.sqrt((left_x - right_x) ** 2 + (left_y - right_y) ** 2)
    sin = opp / hyp
    theta = math.asin(sin) * 57.2958  # Convert radians to degrees
    
    # Step 2: Calculate the center of the image for rotation
    image_center = tuple(np.array(ROI.shape[1::-1]) / 2)
    
    # Step 3: Get the rotation matrix
    rot_mat = cv2.getRotationMatrix2D(image_center, theta, 1.0)
    
    # Step 4: Rotate the image
    rotated_result = cv2.warpAffine(ROI, rot_mat, ROI.shape[1::-1], flags=cv2.INTER_LINEAR)
    
    # Step 5: Adjust the height of the rotated image
    if opp > 0:
        h = rotated_result.shape[0] - opp // 2
    else:
        h = rotated_result.shape[0] + opp // 2
    
    rotated_result = rotated_result[0:h, :]
    
    # Display the result (optional)
    plt.imshow(rotated_result)
    plt.show()
    
    return rotated_result

def crop_license_plate(image_path):
    """Detect and crop license plates from an image."""
    results = model(image_path)  # Run detection on the image

    # Get the results (predictions)
    pred = results.pred[0]  # The first image in the batch
    results.print()

    # Render the detections on the image
    # The .render() method returns a list containing the image with detections
    annotated_image = results.render()[0]

    # Convert the color from RGB (used by YOLO) to BGR (used by OpenCV)
    annotated_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)

    # Display the resulting image
    #cv2.imshow('Custom YOLOv5 Detections', annotated_image_bgr)

    # Wait for a key press to close the window
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    for *xyxy, conf, cls in pred:
        if int(cls) == 0:  # Class '0' for license plates (check YOLO class index)
            # Crop the detected plate from the image
            x1, y1, x2, y2 = map(int, xyxy)
            cropped_img = Image.open(image_path).crop((x1, y1, x2, y2))

            # Convert the cropped image to numpy array for rotation
            cropped_img_np = np.array(cropped_img)

            # Example coordinates for the edges of the detected plate (replace with actual values)
            left_x, left_y = x1, y1  # Example: top-left corner
            right_x, right_y = x2, y1  # Example: top-right corner

            # Call the rotation function to straighten the plate
            rotated_plate = rotate_plate(cropped_img_np, left_x, left_y, right_x, right_y)

            # Save the rotated image
            output_image_path = output_dir / f"plate_{int(time.time())}.jpg"
            cv2.imwrite(str(output_image_path), rotated_plate)

            print(f"Plate detected, rotated, and saved to {output_image_path}")
            return output_image_path  # Return path to the cropped image

    print("No license plate detected.")
    return None

# Example usage:
if __name__ == "__main__":
    image_path = input("Enter the image path: ")
    crop_license_plate(image_path)

