import sqlite3
from sqlite3 import Row, Connection, Cursor
from classes import Lesson
from typing import Sequence
from pathlib import Path


class BotDB:

    def __init__(self, db_file: Path):
        """Connect to database"""
        self.connection: Connection = sqlite3.connect(db_file)
        self.connection.row_factory = Row
        self.cursor: Cursor = self.connection.cursor()

    def user_exists(self, user_id: int) -> bool:
        """User is exists in database"""
        sql_request = 'SELECT "id" FROM "users" WHERE "user_id" = ?'
        result = self.cursor.execute(sql_request, (user_id,))

        return bool(result.fetchone())

    def get_user_group(self, user_id: int) -> str:
        sql_request = 'SELECT "studygroup" FROM users WHERE "user_id" = ?'
        result = self.cursor.execute(sql_request, (user_id,))

        return result.fetchone()['studygroup']

    def get_user_timetable(self, user_id: int) -> list[Row]:
        group = self.get_user_group(user_id)

        sql_request = """SELECT weeknumber, weekday, pairtime, lesson FROM timetable 
        WHERE studygroup = ?
        """
        result = self.cursor.execute(sql_request, (group,))

        return result.fetchall()

    def add_user(self, user_id: int, group: str):
        """Add user to database"""
        sql_request = 'INSERT INTO users ("user_id", "studygroup") VALUES (?, ?)'
        self.cursor.execute(sql_request, (user_id, group))

        self.connection.commit()

    def delete_user(self, user_id: int):
        sql_request = 'DELETE FROM users WHERE "user_id" = ?'
        self.cursor.execute(sql_request, (user_id,))

        self.connection.commit()

    def get_courses(self) -> list[Row]:
        sql_request = 'SELECT DISTINCT course FROM timetable'

        result = self.cursor.execute(sql_request)

        return result.fetchall()

    def get_groups(self, course: str) -> list[Row]:
        """Get group list of course"""
        sql_request = 'SELECT DISTINCT studygroup FROM timetable WHERE course = ?'

        result = self.cursor.execute(sql_request, (course, ))

        return result.fetchall()

    def get_timetable(self, group: str, week_number: int, weekday: str) -> list[Row]:
        sql_request = """SELECT pairtime, lesson FROM timetable 
        WHERE studygroup = ? AND weeknumber = ? AND weekday = ?
        """
        result = self.cursor.execute(sql_request, (group, week_number, weekday))

        return result.fetchall()

    def update_timetable(self, timetable_data: Sequence[Lesson]):
        """Delete and Insert timetable"""
        self.cursor.executescript("""DELETE FROM timetable;
            UPDATE sqlite_sequence SET seq=0 WHERE name = 'timetable'
        """)

        sql_request = """INSERT INTO timetable (course, studygroup, weeknumber, weekday, pairtime, lesson)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.cursor.executemany(sql_request, timetable_data)

        self.connection.commit()

    def close(self):
        """Close database connection"""
        self.connection.close()
