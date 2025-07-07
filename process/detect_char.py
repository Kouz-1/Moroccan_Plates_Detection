from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing import image


try:
    model = load_model('./char_model/char_model_1.h5')
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")


# Define class labels (must match training order)
class_names = ['0', '1', '2', '3', '4', '5','6', '7', '8','9', 'T', 'W', 'A', 'B','D', 'H', 'WAW']
class_names = [c for c in class_names if c != '']  # Remove empty strings if any

def predict_char(img_path):
    model = load_model('./char_model/char_model_1.h5')
    """Load the image, preprocess, and predict the character."""
    # Load and preprocess the image
    img = image.load_img(img_path, target_size=(28, 28))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # shape: (1, 28, 28, 3)

    # Predict
    pred = model.predict(img_array)
    predicted_index = np.argmax(pred)

    # Map to class label
    if predicted_index < len(class_names):
        predicted_label = class_names[predicted_index]
        return predicted_label
    else:
        return None

