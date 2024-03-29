from facesdb import FacesDB
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
db = FacesDB(DATABASE_URL)
# db.create_employee_table()
# db.create_attendance_table()
db.add_user("ahmad ,sayed" , )
print(df.info())