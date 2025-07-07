import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading
import json
import os
import cv2
from process.main import process_image, process_video, process_live_feed

class PlateDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moroccan License Plate Detection & Recognition (KOUZI)")
        self.root.geometry("1100x650")
        self.root.configure(bg="white")

        self.cap = None
        self.current_mode = None
        self.image_path = None
        self.video_path = None

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 10), padding=6)
        style.configure("TLabel", font=("Helvetica", 11))

        self.setup_ui()

    def check_status(self):
        from check_plate_status import check_plate_status
        result = check_plate_status()
        messagebox.showinfo("Plate Status", result)

    def setup_ui(self):
        title = tk.Label(self.root, text="Moroccan License Plate Detection & Recognition (KOUZI)", font=("Helvetica", 16, "bold"), bg="white")
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left panel for buttons
        left_frame = tk.Frame(main_frame, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Button(left_frame, text="Load Image", width=20, command=self.select_image).pack(pady=5)
        ttk.Button(left_frame, text="Load Video", width=20, command=self.select_video).pack(pady=5)
        ttk.Button(left_frame, text="Open Camera", width=20, command=self.start_camera_feed).pack(pady=5)

        ttk.Button(left_frame, text="Start Detection", width=20, command=self.run_detection).pack(pady=15)
        ttk.Button(left_frame, text="Close Camera", width=20, command=self.close_camera).pack(pady=5)
        ttk.Button(left_frame, text="Check Status", width=20, command=self.check_status).pack(pady=5)
        from vehicle_manager import show_vehicle_admin_window
        ttk.Button(left_frame, text="Manage Vehicles", width=20, command=show_vehicle_admin_window).pack(pady=5)

        ttk.Button(left_frame, text="Exit", width=20, command=self.root.quit).pack(pady=20)

        # Right panel for images and result
        right_frame = tk.Frame(main_frame, bg="white")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        detection_label = tk.Label(right_frame, text="Detection:", font=("Helvetica", 12), bg="white")
        detection_label.pack(anchor='center')

        img_frame = tk.Frame(right_frame, bg="white")
        img_frame.pack(pady=10)

        self.input_canvas = tk.Label(img_frame, bg="#e0e0e0", width=300, height=200)
        self.input_canvas.pack(side=tk.LEFT, padx=20)

        self.result_canvas = tk.Label(img_frame, bg="#e0e0e0", width=300, height=200)
        self.result_canvas.pack(side=tk.LEFT, padx=20)

        result_frame = tk.LabelFrame(right_frame, text="Detected Text", font=("Helvetica", 11), bg="white", fg="black")
        result_frame.pack(pady=10, fill=tk.X, padx=20)

        self.result_text = tk.Label(result_frame, text="", font=("Helvetica", 12), bg="white")
        self.result_text.pack(anchor='center', pady=5)

    def select_image(self):
        self.current_mode = "image"
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if self.image_path:
            img = Image.open(self.image_path)
            img = img.resize((300, 200))
            self.input_photo = ImageTk.PhotoImage(img)
            self.input_canvas.config(image=self.input_photo)
            self.input_canvas.image = self.input_photo

    def select_video(self):
        self.current_mode = "video"
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if self.video_path:
            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame = cv2.cvtColor(cv2.resize(frame, (300, 200)), cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                self.input_photo = ImageTk.PhotoImage(img)
                self.input_canvas.config(image=self.input_photo)
                self.input_canvas.image = self.input_photo

    def start_camera_feed(self):
        self.current_mode = "camera"
        self.cap = cv2.VideoCapture(0)
        self.update_camera()

    def update_camera(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(cv2.resize(frame, (300, 200)), cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                self.input_photo = ImageTk.PhotoImage(img)
                self.input_canvas.config(image=self.input_photo)
                self.input_canvas.image = self.input_photo
            self.root.after(30, self.update_camera)

    def close_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def run_detection(self):
        if self.current_mode == "image" and self.image_path:
            threading.Thread(target=self._detect_image, daemon=True).start()
        elif self.current_mode == "video" and self.video_path:
            threading.Thread(target=self._detect_video, daemon=True).start()
        elif self.current_mode == "camera":
            threading.Thread(target=self._detect_camera, daemon=True).start()
        else:
            messagebox.showinfo("Info", "Please select an input first.")

    def _detect_image(self):
        process_image(self.image_path)
        self.show_results()

    def _detect_video(self):
        process_video(self.video_path)
        self.show_results()

    def _detect_camera(self):
        process_live_feed()
        self.show_results()

    def show_results(self):
        if os.path.exists('cropped_plates'):
            files = sorted(os.listdir('cropped_plates'), key=lambda x: os.path.getmtime(os.path.join('cropped_plates', x)), reverse=True)
            if files:
                last_plate = os.path.join('cropped_plates', files[0])
                img = Image.open(last_plate).resize((300, 200))
                photo = ImageTk.PhotoImage(img)
                self.result_canvas.config(image=photo)
                self.result_canvas.image = photo

        plate_info = self.get_last_plate_info()
        self.result_text.config(text=plate_info)
        from store_plate_to_mysql import store_plate_to_mysql
        store_plate_to_mysql()


    def get_last_plate_info(self, json_path='json_plates/plates.json'):
        if not os.path.exists(json_path):
            return "No plate information found."
        with open(json_path, 'r') as f:
            data = json.load(f)
        if isinstance(data, list) and data:
            last = data[-1]
            return f"{last['number']} - {last['char']} - {last['region']}"
        return "Invalid JSON format."

if __name__ == "__main__":
    root = tk.Tk()
    app = PlateDetectorApp(root)
    root.mainloop()
