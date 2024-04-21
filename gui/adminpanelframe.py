import tkinter as tk
from tkinter import ttk
from tkinter import filedialog , messagebox
from tkcalendar import DateEntry as calendar
from dotenv import load_dotenv
import sys
import os
import cv2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import processing as ut
load_dotenv()
DATABASE_URL = '../database/face_recognition.db'

class adminPanelPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # Store the controller for later use
        ### section: Frame Title
        self.write_title("Admin Panel")
        self.vertical_spacing()
        # Section: Register new employee
        self.write_title("Register new employee:")
        self.photo_path = tk.StringVar()  # Variable to store the photo path
        self.name = tk.StringVar()  # Variable to store the name
        name_label = tk.Label(self, text="Name:")
        name_label.pack()
        name_entry = tk.Entry(self, textvariable=self.name)
        name_entry.pack()
        self.browse_button = tk.Button(self, text="Select Image", command=self.browse)
        self.browse_button.pack()
        self.register_button = tk.Button(self, text="Register new ", command=self.register)
        self.register_button.pack()
        path_label = tk.Label(self, textvariable=self.photo_path)
        path_label.pack()
        self.vertical_spacing()
        # Section: Export Attendance
        self.write_title("Export Attendance:")
        self.date_entry = calendar(self)
        self.date_entry.pack()
        export_button = tk.Button(self, text="Export Attendance", command=self.get_attendance)
        export_button.pack()
        self.vertical_spacing()
        # Section: Get employee attendance
        self.write_title("Get Employee Attendance:")
        # add a text box to write the id
        self.get_attendance_id = tk.StringVar()
        get_attendance_label = tk.Label(self, text="Emoplyee's ID:")
        get_attendance_label.pack()
        self.get_attendance_entry = tk.Entry(self, textvariable=self.get_attendance_id)
        self.get_attendance_entry.pack()
        self.get_attendance_button = tk.Button(self, text="Get Attendance", command=self.get_attendance_by_id)
        self.get_attendance_button.pack()
        self.vertical_spacing()
        # Section: Delete employee by ID
        self.write_title("Delete Employee:")
        delete_label = tk.Label(self, text="Delete employee by ID:")
        delete_label.pack()
        self.delete_id = tk.StringVar()
        delete_entry = tk.Entry(self, textvariable=self.delete_id)
        delete_entry.pack()
        delete_button = tk.Button(self, text="Delete", command=self.delete_employee)
        delete_button.pack()
        self.vertical_spacing()
        
        # Section: Return to menu
        ttk.Separator(self, orient="horizontal").pack(fill="x")
        return_button = tk.Button(self, text="Return to Menu", command=self.return_to_menu)
        return_button.pack()
    def write_title(self ,title:str):
        title_label = tk.Label(self, text=title)
        title_label.pack(fill="x")
        ttk.Separator(self, orient="horizontal").pack(fill="x")
    def vertical_spacing(self):
        vertical_space = tk.Label(self, height=1)
        vertical_space.pack()
    def delete_employee(self):
        employee_id = self.delete_id.get()
        if not employee_id:
            messagebox.showinfo("Error", "Please enter the employee ID.")
            return
        successful = self.controller.db.delete_employee_by_id(employee_id)
        if successful:
            messagebox.showinfo("Success", f"Deleted employee with ID: {employee_id}")
        else:
            messagebox.showinfo("Error", f"No employee found with ID: {employee_id}")
        self.delete_id.set('')       
    def browse(self):
        self.photo_path.set(filedialog.askopenfilename(
            filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg ")]))  # Open the dialog and store the selected path
    def return_to_menu(self):
        self.controller.show_start_page()
    def register(self):
        photo_path = self.photo_path.get()
        name = self.name.get()
        if not name:
            messagebox.showinfo("Error", "Please enter the name.")
            return
        if not os.path.exists(photo_path):
            messagebox.showinfo("Error", "Please select a valid image.")
            return
        if photo_path and name:
            self.register_button.config(state="disabled")
            img = cv2.imread(photo_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            embedding = ut.get_embeddings(img)
            if embedding is None:
                messagebox.showinfo("Error", "No face detected in the image.")
                self.register_button.config(state="normal")
                return
            embedding = embedding[0]["embedding"]
            str_embedding = ut.np_ndarrray_to_str(embedding)
            successful =  self.controller.db.add_user(name, str_embedding)
            if not successful:
                messagebox.showinfo("Error", "An error occurred while registering the employee.")
                self.register_button.config(state="normal")
                return
            else:
                messagebox.showinfo("Success", f"Employee {name}: with photo {photo_path},was successfully registered.")
                print(f"Registered photo: {photo_path}, name: {name}")
            self.photo_path.set('')
            self.register_button.config(state="normal")
    def get_attendance(self):
        date = str(self.date_entry.get_date())
        attendance = self.controller.db.get_employees_attendance_by_date(date)
        date_for_path = date.replace("-" , ".")
        csv_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile=f"attendance_{date_for_path}")
        attendance.to_csv(csv_path, index=False)
    def get_attendance_by_id(self):
        id = str(self.get_attendance_entry.get())
        if not id:
            messagebox.showinfo("Error", "Please enter the employee ID.")
            return
        attendance = self.controller.db.get_employee_attendance_by_id(id)
        if attendance.empty:
            messagebox.showinfo("Error", f"No attendance records found for employee with ID: {id}")
            return
        csv_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile=f"attendance_No_{id}")
        attendance.to_csv(csv_path, index=False)