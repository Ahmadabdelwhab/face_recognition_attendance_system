from streamlit_webrtc import webrtc_streamer
from facesdb import FacesDB
import utils as ut
import os
from dotenv import load_dotenv
import av
import cv2
from time import sleep
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
db = FacesDB(DATABASE_URL)
employees_db = db.get_employees()
employees = ut.load_employees(employees_db)
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
class VideoProcessor:
    def recv(self , frame):
        # Process the frame here
        frm = frame.to_ndarray(format='bgr24')
        processed_frame , employees_ids = ut.process_frame(frm , employees)
        if employees_ids:
            for employee_id in employees_ids:
                db.add_attendance(employee_id)
        return av.VideoFrame.from_ndarray(processed_frame , format='bgr24')
webrtc_streamer(key="key" , video_processor_factory=VideoProcessor )