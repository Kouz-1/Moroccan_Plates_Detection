import cv2
import os
import glob
from process.segment_characters import segment_characters
from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing import image
from process.detect_char import predict_char
from process.save_plate_json import save_plate_to_json

# Define output folders
cropped_plate_folder = 'cropped_plates'
char_folder = 'char'

# Ensure the 'char' folder exists
os.makedirs(char_folder, exist_ok=True)

# Define class labels (must match training order)
class_names = ['0', '1', '2', '3', '4', '5','6', '7', '8','9', 'T', 'W', 'A', 'B','D', 'H', 'WAW']
class_names = [c for c in class_names if c != '']

def clear_char_folder(folder_path='char'):
    files = glob.glob(os.path.join(folder_path, '*'))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Failed to delete {f}: {e}")
            
def process_plate(cropped_plate_path):
    """Process cropped license plate image."""
    clear_char_folder()  # Clear old character images before processing
    # Load cropped license plate image
    image = cv2.imread(str(cropped_plate_path))

    if image is None:
        print("Image not found.")
        return

    # Step 1: Segment characters
    characters = segment_characters(image)

    # Step 2: Save segmented characters and predict them
    for i, char_img in enumerate(characters):
        # Save character image to 'char' folder
        char_image_path = os.path.join(char_folder, f'char_{i}.png')
        cv2.imwrite(char_image_path, char_img)

        # Step 3: Predict character label using the trained model
        predicted_label = predict_char(char_image_path)

        # Step 4: Write prediction to text file
        with open('predictions.txt', 'a') as f:
            f.write(f"Character {i}: {predicted_label}\n")
            print(f'Character {i}: Predicted label: {predicted_label}')
            
    # After all characters are predicted and saved to predictions.txt
    save_plate_to_json()


