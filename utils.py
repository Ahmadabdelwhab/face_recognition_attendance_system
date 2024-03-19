from PIL import Image
import numpy as np
import sqlite3
import cv2
import os
from deepface import DeepFace
from typing import List, Tuple , Dict
import json
### create sqlite3 database and table for emplpyoees
DATABASE_URL = "./database/face_recognition.db"

#### data base functions ###################
def create_employee_table():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    date_of_day DATE DEFAULT (DATE(CURRENT_TIMESTAMP)),
                    time_in TIME DEFAULT (TIME(CURRENT_TIMESTAMP)),
                    last_seen TIME DEFAULT (TIME(CURRENT_TIMESTAMP)),
                    UNIQUE(employee_id, date_of_day),
                    FOREIGN KEY(employee_id) REFERENCES employees(id)
                )
                ''')
    conn.commit()
    conn.close()
def create_attendance_table(connection:sqlite3.Connection):
    conn = connection
    c = conn.cursor()
    c.execute(f'''CREATE TABLE  IF NOT EXISTS attendance 
                (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                date DATETIME NOT NULL,
                time TEXT NOT NULL
                )''')
    conn.commit()
def add_user(name:str , embedding:str , connection:sqlite3.Connection):
    #add user to database
    conn = connection
    c = conn.cursor()
    c.execute("INSERT INTO employees (name, embedding) VALUES (?, ?)", (name, embedding))
    conn.commit()
def get_employees(connection:sqlite3.Connection)-> Tuple[List[int | str]]:
    #get embedding of image
    conn = connection
    c = conn.cursor()
    c.execute("SELECT id , name , embedding FROM employees")
    rows = c.fetchall()
    return rows
def add_attendance(employee_id: int, connection: sqlite3.Connection):
    """
    Records the attendance of an employee.

    Args:
        employee_id (int): The ID of the employee.
        connection (sqlite3.Connection): The connection to the SQLite database.

    Returns:
        None
    """
    c = connection.cursor()
    # Check if an attendance record for the employee and the current date already exists
    c.execute("SELECT * FROM attendance WHERE employee_id = ? AND date_of_day = DATE(CURRENT_TIMESTAMP)", (employee_id,))
    result = c.fetchone()
    # If the record exists, update the last_seen field
    if result is not None:
        c.execute("UPDATE attendance SET last_seen = TIME(CURRENT_TIMESTAMP) WHERE employee_id = ? AND date_of_day = DATE(CURRENT_TIMESTAMP)", (employee_id,))
    # If the record doesn't exist, insert a new one
    else:
        c.execute("INSERT INTO attendance (employee_id, date_of_day, time_in, last_seen) VALUES (?, DATE(CURRENT_TIMESTAMP), TIME(CURRENT_TIMESTAMP), TIME(CURRENT_TIMESTAMP))", (employee_id,))
    connection.commit()
############################################

#### pre-processing functions ##############
def str_to_np_ndarray(s:str) -> np.ndarray:
    list_embedding = json.loads(s)
    embedding = np.array(list_embedding)
    return embedding
def load_employees(employees:Tuple[list[int|str]]) -> Dict[id , List[str|np.ndarray]]:
    employees_dict = {}
    for employee in employees:
        id , name , str_embedding = employee
        embedding = str_to_np_ndarray(str_embedding)
        employees_dict[id] = [name , embedding]
    return employees_dict
def np_ndarrray_to_str(embedding:np.ndarray) -> str:
    list_embedding = embedding.tolist()
    str_embedding = json.dumps(list_embedding)
    return str_embedding