import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
from dotenv import load_dotenv
from facesdb import FacesDB
import utils as ut
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.attributes('-fullscreen', True)
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor='center')
        self.frames = {}
        for F in (StartPage, RecordingPage, RegisterPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            if F == RecordingPage:
                self.recording_page = frame
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # Store the controller for later use
        label = tk.Label(self, text="Start Page")
        label.pack(pady=10, padx=10)
        button1 = tk.Button(self, text="Recording Page",
                            command=lambda: controller.show_frame(RecordingPage))
        button1.pack()
        button2 = tk.Button(self, text="Register New Employee",
                            command=lambda: controller.show_frame(RegisterPage))
        button2.pack()
        exit_button = tk.Button(self, text="Exit", command=self.exit_app)
        exit_button.pack()
    def exit_app(self):
        self.controller.recording_page.db.close_connection()  # Close the database connection
        self.quit() 
class RecordingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # Store the controller for later use
        self.canvas = tk.Canvas(self, width=1440, height=810)
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
        self.controller.show_frame(StartPage)

    def video_capture(self):
        
        cap = cv2.VideoCapture(0)
        while self.recording:
            ret, frame = cap.read()
            if not ret:
                break
            processed_frame , employees_ids = ut.process_frame(frame , self.employees)
            if employees_ids:
                for employee_id in employees_ids:
                    self.db.add_attendance(employee_id)
                    print(f"Employee with ID {employee_id} has been recognized.")
            rgb_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_image)# Resize the image to fit the canvas
            pil_img_resized = pil_img.resize((1440, 810))
            imgtk = ImageTk.PhotoImage(image=pil_img_resized)
            self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
            self.canvas.image = imgtk
        cap.release()

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Register Page")
        label.pack(pady=10, padx=10)
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

app = Application()
app.mainloop()
