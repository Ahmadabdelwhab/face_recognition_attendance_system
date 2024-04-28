import tkinter as tk
from .recordingpageframe import RecordingPage
from .adminpanelframe import adminPanelPage
from .startpageframe import StartPage
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.facesdb import FacesDB
DATABASE_URL = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'face_recognition.db'))
class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.attributes('-fullscreen', True)
        self.db = FacesDB(DATABASE_URL)
        self.start_page = StartPage(parent=self, controller=self)
        self.recording_page = RecordingPage(parent=self, controller=self)
        self.admin_page = adminPanelPage(parent=self, controller=self)
        self.current_frame = self.start_page
        self.current_frame.pack()
    def show_start_page(self):
        self.current_frame.pack_forget()
        self.current_frame = self.start_page
        self.current_frame.pack()
    def show_recording_page(self):
        self.current_frame.pack_forget()
        self.current_frame = self.recording_page
        self.current_frame.pack()
    def show_admin_page(self):
        self.current_frame.pack_forget()
        self.current_frame = self.admin_page
        self.current_frame.pack()
    def close_app(self):
        self.db.close_connection()
        self.destroy()
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
    app.db.close_connection()
