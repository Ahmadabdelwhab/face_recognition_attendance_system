'''The recording page frame is used to display the video feed from the webcam and process the frames to recognize employees.'''
import tkinter as tk
import cv2
import threading # type: ignore
from PIL import Image, ImageTk
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import processing as ut
from utils.facesdb import FacesDB
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'face_recognition.db'))

class RecordingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # Store the controller for later use
        self.canvas = tk.Canvas(self, width=100, height=100)
        self.canvas.pack(anchor='center')
        self.recording = False
        self.button1 = tk.Button(self, text="Start Recording",
                            command=self.start_recording)
        self.button1.pack()
        self.button2 = tk.Button(self, text="Back to Home",
                            command=self.stop_recording_and_go_home)
        self.button2.pack()
        self.db = FacesDB(DATABASE_URL)  # Create a new database connection
        db_employees = self.db.get_employees()
        self.employees = ut.load_employees(db_employees)

    def start_recording(self):
        if self.recording:
            self.recording = False
            self.button1.config(text="Start Recording")
        else:   
            self.recording = True
            self.button1.config(text="Stop Recording")  # Change the button text,
            threading.Thread(target=self.video_capture).start()

    def stop_recording_and_go_home(self):
            self.recording = False
            self.button1.config(text="Start Recording")  # Change the button text,
            self.controller.show_start_page()
        

    def video_capture(self):
        cap = cv2.VideoCapture(0)
        image_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        image_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.canvas.config(width=int(image_width * 0.6), height=int(image_height * 0.6))
        while self.recording:
            ret, frame = cap.read()
            frame = cv2.resize(frame, (int(image_width * 0.6), int(image_height * 0.6)))
            if not ret:
                break
            processed_frame , employees_ids = ut.process_frame(frame , self.employees)
            if employees_ids:
                for employee_id in employees_ids:
                    self.db.add_attendance(employee_id)
                    print(f"Employee with ID {employee_id} has been recognized.")
            rgb_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_image)
            imgtk = ImageTk.PhotoImage(image=pil_img)
            self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
            self.canvas.image = imgtk
        cap.release()