from facesdb import FacesDB
import processing as ut
import os
from dotenv import load_dotenv
import numpy as np
import cv2
import time
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
db = FacesDB(DATABASE_URL)
employees_db = db.get_employees()
employees = ut.load_employees(employees_db)
        
def main():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # frame = cv2.resize(frame, (0, 0), fx=1, fy=0)
        processed_frame , employees_ids = ut.process_frame(frame , employees)
        if employees_ids:
            for employee_id in employees_ids:
                db.add_attendance(employee_id)
        height, width, _ = frame.shape
        print(f'Frame size: {width}x{height}')
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f'Frame rate: {fps} FPS') 
        cv2.imshow('Frame', processed_frame)

        if cv2.waitKey(1) == ord('q'):
            break
        time.sleep(1/24)  # Pause execution for approximately 1/10th of a second
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    main()
    db.conn.close()




