from facesdb import FacesDB
import utils as ut
import os
from dotenv import load_dotenv
import numpy as np
import cv2
import time
from typing import Dict  , List  , Tuple
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
db = FacesDB(DATABASE_URL)
employees_db = db.get_employees()
employees = ut.load_employees(employees_db)

        
def main():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (0, 0), fx=0.3, fy=0.3)
        processed_frame , _ = ut.preprocess_frame(frame)
        height, width, _ = frame.shape
        print(f'Frame size: {width}x{height}')
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f'Frame rate: {fps} FPS')
        cv2.imshow('Frame', processed_frame)

        if cv2.waitKey(1) == ord('q'):
            break
        time.sleep(1/15)  # Pause execution for approximately 1/10th of a second
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()




