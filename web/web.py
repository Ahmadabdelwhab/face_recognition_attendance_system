from streamlit_webrtc import webrtc_streamer , MediaStreamConstraints
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.facesdb import FacesDB
import utils.processing as ut
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
        print(frm.shape)
        processed_frame , employees_ids = ut.process_frame(frm , employees)
        if employees_ids:
            for employee_id in employees_ids:
                db.add_attendance(employee_id)
        # sleep(1)
        return av.VideoFrame.from_ndarray(processed_frame , format='bgr24')

# Define the video constraints
constraints = MediaStreamConstraints({
        "video": {
            "width": {"min": 640 , "ideal": 1280 , "max": 1920},
            "height": {"min": 480 , "ideal": 720 , "max": 1080},
            "frameRate": {"ideal": 24 , "max": 30 , "min": 15}
        }
    })
webrtc_streamer(key="key" , video_processor_factory=VideoProcessor , rtc_configuration={  # Add this config
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }, media_stream_constraints=constraints )