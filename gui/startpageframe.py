

import tkinter as tk
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # Store the controller for later use
        label = tk.Label(self, text="Start Page")
        label.pack(pady=10, padx=10)
        button1 = tk.Button(self, text="Recording Page",
                            command=lambda: controller.show_recording_page())
        button1.pack()
        button2 = tk.Button(self, text="adminPage",
                            command=lambda: controller.show_admin_page())
        button2.pack()
        exit_button = tk.Button(self, text="Exit", command=self.controller.close_app)
        exit_button.pack()