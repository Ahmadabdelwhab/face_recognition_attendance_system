import tkinter as tk
from tkinter import filedialog , messagebox
from tkcalendar import DateEntry as calendar
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
        self.date_entry = calendar(self)
        self.date_entry.pack()
        export_button = tk.Button(self, text="Export Attendance", command=self.get_attendance)
        export_button.pack()
        exit_button = tk.Button(self, text="Exit", command=self.exit_app)
        exit_button.pack()
    def get_attendance(self):
        date = str(self.date_entry.get_date())
        attendance = self.controller.recording_page.db.get_employees_attendance_by_date(date)
        date_for_path = date.replace("-" , ".")
        csv_path = f"attendance_{date_for_path}.csv"
        attendance.to_csv(csv_path, index=False)
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

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # Store the controller for later use
        self.photo_path = tk.StringVar()  # Variable to store the photo path
        self.name = tk.StringVar()  # Variable to store the name

        name_label = tk.Label(self, text="Name:")
        name_label.pack()

        name_entry = tk.Entry(self, textvariable=self.name)
        name_entry.pack()

        browse_button = tk.Button(self, text="Browse", command=self.browse)
        browse_button.pack()

        register_button = tk.Button(self, text="Register", command=self.register)
        register_button.pack()
        path_label = tk.Label(self, textvariable=self.photo_path)
        path_label.pack()
        return_button = tk.Button(self, text="Return to Menu", command=self.return_to_menu)
        return_button.pack()
        

    def browse(self):
        self.photo_path.set(filedialog.askopenfilename())  # Open the dialog and store the selected path
    def return_to_menu(self):
        self.controller.show_frame(StartPage)
    def register(self):
        photo_path = self.photo_path.get()
        name = self.name.get()
        if photo_path and name:
            img = cv2.imread(photo_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            embedding = ut.get_embeddings(img)
            if embedding is None:
                messagebox.showinfo("Error", "No face detected in the image.")
                return
            embedding = embedding[0]["embedding"]
            str_embedding = ut.np_ndarrray_to_str(embedding)
            self.controller.recording_page.db.add_user(name, str_embedding)
            print(f"Registered photo: {photo_path}, name: {name}")
            self.photo_path.set('')
def main():
    app = Application()
    app.mainloop()
if __name__ == "__main__":
    main()
