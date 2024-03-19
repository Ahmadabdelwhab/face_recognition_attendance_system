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
    """
    Creates the 'attendance' table in the database if it doesn't exist.
    The table stores the attendance records of employees, including their ID, date of day, time in, and last seen time.
    """
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''
                CREATE TABLE IF NOT EXISTS employee (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
                ''')
    conn.commit()
    conn.close()
def create_attendance_table(connection:sqlite3.Connection):
    """
    Creates the 'attendance' table in the database if it doesn't exist.

    Args:
        connection (sqlite3.Connection): The SQLite database connection object.

    Returns:
        None
    """

    conn = connection
    c = conn.cursor()
    c.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    employee_id INTEGER,
                    date_of_day DATE DEFAULT (DATE(CURRENT_TIMESTAMP)),
                    time_in TIME DEFAULT (TIME(CURRENT_TIMESTAMP)),
                    last_seen TIME DEFAULT (TIME(CURRENT_TIMESTAMP)),
                    UNIQUE(employee_id, date_of_day),
                    FOREIGN KEY(employee_id) REFERENCES employees(id)
                )
                ''')
    conn.commit()
def add_user(name:str , embedding:str , connection:sqlite3.Connection):
    """
    Add a new user to the employees table in the database.

    Args:
        name (str): The name of the user.
        embedding (str): The embedding of the user.
        connection (sqlite3.Connection): The connection to the SQLite database.

    Returns:
        None
    """
    conn = connection
    c = conn.cursor()
    c.execute("INSERT INTO employees (name, embedding) VALUES (?, ?)", (name, embedding))
    conn.commit()
def get_employees(connection: sqlite3.Connection) -> Tuple[List[int | str]]:
    """
    Retrieve a list of employees from the database.

    Args:
        connection (sqlite3.Connection): The connection to the SQLite database.

    Returns:
        Tuple[List[int | str]]: A tuple containing a list of employee records. Each record is a tuple
        containing the employee's ID (int), name (str), and embedding (str).
        
    """
    conn = connection
    c = conn.cursor()
    c.execute("SELECT id, name, embedding FROM employees")
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
def str_to_np_ndarray(s: str) -> np.ndarray:
    """
    Convert a string representation of a list to a NumPy ndarray.

    Args:
        s (str): The string representation of a list.

    Returns:
        np.ndarray: The NumPy ndarray representation of the list.

    Example:
        str_to_np_ndarray('[1, 2, 3]')
        array([1, 2, 3])
    """
    list_embedding = json.loads(s)
    embedding = np.array(list_embedding)
    return embedding
def load_employees(employees: Tuple[List[int|str]]) -> Dict[int, List[str|np.ndarray]]:
    """
    Load employees' information into a dictionary.

    Args:
        employees (Tuple[List[int|str]]): A tuple of lists containing employee information.
            Each list should contain the employee's ID, name, and string representation of their embedding.

    Returns:
        Dict[int, List[str|np.ndarray]]: A dictionary where the employee ID is the key and the value is a list
            containing the employee's name and embedding.

    """
    employees_dict = {}
    for employee in employees:
        id, name, str_embedding = employee
        embedding = str_to_np_ndarray(str_embedding)
        employees_dict[id] = [name, embedding]
    return employees_dict
def np_ndarrray_to_str(embedding: np.ndarray) -> str:
    """
    Convert a NumPy ndarray to a string representation.

    Args:
        embedding (np.ndarray): The NumPy ndarray to be converted.

    Returns:
        str: The string representation of the ndarray.
    """
    list_embedding = embedding.tolist()
    str_embedding = json.dumps(list_embedding)
    return str_embedding