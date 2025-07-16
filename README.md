Moroccan License Plate Detection and Recognition

Introduction

This project presents a complete pipeline for detecting and recognizing Moroccan license plates from images or video streams using deep learning models.

One particular aspect of Moroccan license plates is the presence of Arabic letters. To make recognition easier and consistent, these Arabic characters are converted to Latin letters using a predefined mapping.
Arabic Letter	Latin Equivalent

Alif (ا)  A

Ba (ب)	B

Jim (ج)	J

Waw (و) W

Dal (د) D
...

The process is divided into multiple key stages, as shown in the following pipeline:

![Screenshot from 2025-07-08 10-51-06](https://github.com/user-attachments/assets/c09ce21e-bb48-4cfa-a9ce-7eb4906a6362)



Step-by-Step Pipeline
1. Acquisition de l’image ou du flux vidéo

The system takes input either as a static image or a live video stream from a camera. This step captures the raw data for processing.

![image](https://github.com/user-attachments/assets/5e8ca6f7-0710-4272-bd4e-97e00c039551)



2. Détection de la plaque avec YOLOv5

We use a YOLOv5 object detection model trained specifically to detect Moroccan license plates. This model identifies and crops the region containing the plate.

![Screenshot from 2025-07-08 12-28-32](https://github.com/user-attachments/assets/bc06a581-d9b6-4047-85d4-58903719a274)



3. Prétraitement de l’image de la plaque

Before character segmentation, the plate image undergoes preprocessing such as grayscale conversion, resizing, and noise reduction to improve accuracy.

4. Segmentation des caractères

Each character in the plate is segmented individually using image processing techniques (like contour detection or projection methods).

![image](https://github.com/user-attachments/assets/402be95b-d839-4d40-ae09-be0de369db3d)

![image](https://github.com/user-attachments/assets/fe4636d0-8895-4a35-8ffd-a244cea9db33)



5. Lecture des caractères avec un modèle CNN

A CNN (Convolutional Neural Network) is used to classify each segmented character. This step performs Optical Character Recognition (OCR) for the license plate.

![image](https://github.com/user-attachments/assets/6b45c50d-4256-44f6-9f2e-1b5bacc47b0a)



6. Stockage des résultats

Finally, the recognized plate number is stored or displayed in a human-readable format, and can be saved to a file, database, or used in further processing.

![image](https://github.com/user-attachments/assets/2356a596-2f1d-4e3e-af8e-4ad5ca7e4bf5)



The system includes a user-friendly GUI built with Tkinter, allowing users to interact with the detection model through a series of simple buttons and actions.

GUI Options :

Load Image	: Load a static image from your computer for plate detection.

Load Video	: Select a video file containing a vehicle for processing.

Open Camera	: Launch your webcam or external camera to capture real-time video.

Start Detection	: Run the YOLOv5 model on the selected image, video, or live camera feed.

Close Camera : Stop the webcam feed and release the video stream.

Check Status : After plate recognition, this button checks if the plate is legal or listed in a database. It displays a status message (e.g., "ENFREINT DE LOIX" = Violates the law).

Exit : Close the application.


Example Output

    Detected Plate: 82227 - A - 6
    Status: ENFREINT DE LOIX (indicates a vehicle not compliant with regulations)


![Screenshot from 2025-07-08 12-29-30](https://github.com/user-attachments/assets/4e6b8184-ba02-4572-81ea-125128e23017)



Tech Stack

    Python
    OpenCV
    YOLOv5
    PyTorch
    TensorFlow / Keras (for CNN)
    Tkinter (for GUI)



