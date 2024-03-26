from facesdb import FacesDB as fd
from dotenv import load_dotenv
import os
load_dotenv()
DB_URL = os.getenv("DATABASE_URL") if os.getenv("DATABASE_URL") else "facedb.db"

db = fd(DB_URL)
db.create_employee_table()
db.create_attendance_table()