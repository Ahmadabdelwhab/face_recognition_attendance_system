import tkinter as tk
from .recordingpageframe import RecordingPage
from .adminpanelframe import adminPanelPage
from .startpageframe import StartPage
DATABASE_URL = '../database/face_recognition.db'
class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.attributes('-fullscreen', True)
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

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
