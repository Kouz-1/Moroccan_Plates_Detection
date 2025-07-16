import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading
import json
import os
import cv2
from process.main import process_image, process_video, process_live_feed

def get_last_plate_info(json_path='json_plates/plates.json'):
    if not os.path.exists(json_path):
        return "No plate information found."
    with open(json_path, 'r') as f:
        data = json.load(f)
    if isinstance(data, list) and data:
        last = data[-1]
        return f"{last['number']} - {last['char']} - {last['region']}"
    return "Invalid JSON format."

class PlateDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Plate Recognition")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")

        self.cap = None  # For camera
        self.current_mode = None  # Track selected mode

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("TLabel", font=("Helvetica", 12))

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="Select Input Type", background="#f5f5f5").pack(pady=10)

        self.button_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.button_frame.pack()

        self.image_button = ttk.Button(self.button_frame, text="Image", command=self.select_image)
        self.image_button.grid(row=0, column=0, padx=10)

        self.video_button = ttk.Button(self.button_frame, text="Video", command=self.select_video)
        self.video_button.grid(row=0, column=1, padx=10)

        self.camera_button = ttk.Button(self.button_frame, text="Camera Feed", command=self.start_camera_feed)
        self.camera_button.grid(row=0, column=2, padx=10)

        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=10, fill=tk.X, padx=20)

        self.input_display = tk.Label(self.root, bg="#e0e0e0", text="Input Preview", width=300, height=200)
        self.input_display.pack(pady=10)

        self.image_label = tk.Label(self.root, bg="#f5f5f5")
        self.image_label.pack(pady=10)

        self.result_label = ttk.Label(self.root, text="Result will appear here", background="#f5f5f5")
        self.result_label.pack(pady=10)

        self.log_text = tk.Text(self.root, height=8)
        self.log_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def disable_buttons(self, exclude=None):
        # Keep all buttons enabled so user can click anytime
        self.image_button.config(state=tk.NORMAL)
        self.video_button.config(state=tk.NORMAL)
        self.camera_button.config(state=tk.NORMAL)

    def stop_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    def reset_mode(self, new_mode):
        if self.current_mode == "camera" and new_mode != "camera":
            self.stop_camera()
        self.current_mode = new_mode
        self.disable_buttons(exclude=new_mode)

    def select_image(self):
        self.reset_mode("image")
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if file_path:
            self.run_processing(lambda: self.process_image(file_path))
        else:
            self.current_mode = None
            self.disable_buttons()

    def select_video(self):
        self.reset_mode("video")
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if file_path:
            self.run_processing(lambda: self.process_video(file_path))
        else:
            self.current_mode = None
            self.disable_buttons()

    def start_camera_feed(self):
        self.reset_mode("camera")
        self.run_processing(self.process_camera)

    def run_processing(self, func):
        self.progress.start()
        threading.Thread(target=self.threaded_run, args=(func,), daemon=True).start()

    def threaded_run(self, func):
        try:
            func()
            self.show_last_cropped_plate()
            result = get_last_plate_info()
            self.result_label.config(text=result)
            self.log("Processing completed.")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.progress.stop()

    def show_last_cropped_plate(self):
        if not os.path.exists('cropped_plates'):
            return
        files = sorted(os.listdir('cropped_plates'), key=lambda x: os.path.getmtime(os.path.join('cropped_plates', x)), reverse=True)
        if not files:
            return
        last_plate = os.path.join('cropped_plates', files[0])
        image = Image.open(last_plate)
        image = image.resize((300, 150))
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

    def process_image(self, path):
        self.log(f"Processing image: {path}")
        img = Image.open(path)
        img = img.resize((300, 200))
        photo = ImageTk.PhotoImage(img)
        self.input_display.config(image=photo)
        self.input_display.image = photo
        process_image(path)

    def process_video(self, path):
        self.log(f"Processing video: {path}")
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (300, 200))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(img)
            self.input_display.config(image=photo)
            self.input_display.image = photo
        cap.release()
        process_video(path)

    def process_camera(self):
        self.log("Starting camera feed...")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.log("Failed to open camera.")
            messagebox.showerror("Error", "Cannot open camera")
            self.current_mode = None
            return
        self.update_camera_feed()

    def update_camera_feed(self):
        if self.cap and self.cap.isOpened() and self.current_mode == "camera":
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (300, 200))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(img)
                self.input_display.config(image=photo)
                self.input_display.image = photo
            # Schedule the next frame update after 30 ms (~33 fps)
            self.root.after(30, self.update_camera_feed)
        else:
            # If camera stopped or mode changed, release camera
            if self.cap:
                self.cap.release()
                self.cap = None


if __name__ == "__main__":
    root = tk.Tk()
    app = PlateDetectorApp(root)
    root.mainloop()
