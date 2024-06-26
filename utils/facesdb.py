import sqlite3
from typing import List, Tuple ,Dict , Any # type: ignore
import pandas as pd
import os
class FacesDB:
    def __init__(self , db_path:str):
        self.conn = sqlite3.connect(db_path , check_same_thread=False)
    def create_employee_table(self):
        """
        Creates the 'attendance' table in the database if it doesn't exist.
        The table stores the attendance records of employees, including their ID, date of day, time in, and last seen time.
        """
        c = self.conn.cursor()
        c.execute('''
                    CREATE TABLE IF NOT EXISTS employee (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        embedding TEXT NOT NULL
                    )
                    ''')
        self.conn.commit()
    def create_attendance_table(self):
        """
        Creates the 'attendance' table in the database if it doesn't exist.

        Args:
            connection (sqlite3.Connection): The SQLite database connection object.

        Returns:
            None
        """

        
        c = self.conn.cursor()
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
        self.conn.commit()
    def add_user(self ,name:str , embedding:str):
        """
        Add a new user to the employees table in the database.

        Args:
            name (str): The name of the user.
            embedding (str): The embedding of the user.
            connection (sqlite3.Connection): The connection to the SQLite database.

        Returns:
            None
        """
        
        c = self.conn.cursor()
        c.execute("INSERT INTO employee (name, embedding) VALUES (?, ?)", (name, embedding))
        self.conn.commit()
    def get_employees(self) -> Tuple[List[int | str]]:
        """
        Retrieve a list of employees from the database.

        Args:
            connection (sqlite3.Connection): The connection to the SQLite database.

        Returns:
            Tuple[List[int | str]]: A tuple containing a list of employee records. Each record is a tuple
            containing the employee's ID (int), name (str), and embedding (str).
            
        """

        c = self.conn.cursor()
        c.execute("SELECT id, name, embedding FROM employee")
        rows = c.fetchall()
        return rows
    def add_attendance(self ,employee_id: int):
        """
        Records the attendance of an employee.

        Args:
            employee_id (int): The ID of the employee.
            connection (sqlite3.Connection): The connection to the SQLite database.

        Returns:
            None
        """
        c = self.conn.cursor()
        # Check if an attendance record for the employee and the current date already exists
        c.execute("SELECT * FROM attendance WHERE employee_id = ? AND date_of_day = DATE(CURRENT_TIMESTAMP)", (employee_id,))
        result = c.fetchone()
        # If the record exists, update the last_seen field
        if result is not None:
            c.execute("UPDATE attendance SET last_seen = TIME(CURRENT_TIMESTAMP) WHERE employee_id = ? AND date_of_day = DATE(CURRENT_TIMESTAMP)", (employee_id,))
        # If the record doesn't exist, insert a new one
        else:
            c.execute("INSERT INTO attendance (employee_id, date_of_day, time_in, last_seen) VALUES (?, DATE(CURRENT_TIMESTAMP), TIME(CURRENT_TIMESTAMP), TIME(CURRENT_TIMESTAMP))", (employee_id,))
        self.conn.commit()
    def get_attendance(self) -> Tuple[List[int | str]]:
        """"""
        c = self.conn.cursor()
        c.execute("""SELECT * FROM attendance
                    SORT BY date_of_day DESC, last_seen DESC
                    """)
        rows = c.fetchall()
        return rows
    def get_employee_attendance(self ,employee_id:int) -> Tuple[List[int | str]]:
        """"""
        c = self.conn.cursor()
        c.execute("""SELECT * FROM attendance
                    WHERE employee_id = ?
                    SORT BY date_of_day DESC, last_seen DESC
                    """, (employee_id,))
        rows = c.fetchall()
        return rows
    def get_attendance_by_date(self ,date:str) -> Tuple[List[int | str]]:
        """"""
        c = self.conn.cursor()
        c.execute("""SELECT * FROM attendance
                    WHERE date_of_day = ?
                    SORT BY date_of_day DESC, last_seen DESC
                    """, (date,))
        rows = c.fetchall()
        return rows
    def get_employee_attendance_by_id(self , employee_id:str) -> pd.DataFrame:
        query = f"""SELECT 
                    all_dates.date_of_day,
                    CASE 
                        WHEN attendance.employee_id = {employee_id} THEN 'Present'
                        ELSE 'Absent'
                    END AS attendance_status,
                    CASE 
                        WHEN attendance.employee_id = {employee_id} THEN 
                            ROUND((julianday(attendance.last_seen) - julianday(attendance.time_in)) * 24, 2)
                        ELSE
                            0
                    END AS hours_worked
                FROM
                    (SELECT DISTINCT date_of_day FROM attendance) AS all_dates
                LEFT JOIN
                    attendance ON all_dates.date_of_day = attendance.date_of_day
                ORDER BY
                    all_dates.date_of_day;
                    """
        attendance_df= pd.read_sql_query(query , self.conn)
        return attendance_df
    def get_employees_attendance_by_date(self , date:str) -> pd.DataFrame:
        query = f"""SELECT  e.id  as ID, e.name as Name, COALESCE(a.time_in , "N/A") as CheckIn, COALESCE(a.last_seen , "N/A") as LastSeen
                    FROM employee AS e
                    LEFT JOIN attendance AS a on a.employee_id = e.id AND a.date_of_day = "{date}"
                    
                    """
        return pd.read_sql_query(query , self.conn)
    def delete_employee_by_id(self , employee_id:str) -> bool:
            """Deletes an employee from the database based on their ID.

            Args:
                employee_id (str): The ID of the employee to be deleted.
            """
            c = self.conn.cursor()
            c.execute("DELETE FROM employee WHERE id = ?", (employee_id,))
            self.conn.commit()
            return c.rowcount > 0
    def close_connection(self):
        """
        Close the connection to the database.

        Args:
            connection (sqlite3.Connection): The connection to the SQLite database.

        Returns:
            None
        """
        self.conn.close()
    def reset_db(self , db_path:str):
        """
        Reset the database by deleting all records in the 'attendance' table.

        Args:
            connection (sqlite3.Connection): The connection to the SQLite database.

        Returns:
            None
        """
        if os.path.exists(db_path):
            os.remove(db_path)
        self.__init__(db_path)
        self.create_employee_table()
        self.create_attendance_table()
        self.conn.commit()
        self.close_connection()
def main():
    pass
if __name__ == "__main__":
    main()