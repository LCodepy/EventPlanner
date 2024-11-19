import datetime
import pickle
import sqlite3
from dataclasses import dataclass

from src.utils.assets import Assets


@dataclass
class CalendarEvent:

    date: datetime.date
    time: datetime.time
    description: str
    color: str
    is_recurring: bool


class CalendarModel:

    def __init__(self) -> None:
        self.database_name = "calendar"
        self.conn = sqlite3.connect(Assets().calendar_database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.database_name} (
                date BLOB NOT NULL,
                time BLOB NOT NULL,
                description TEXT,
                color TEXT,
                is_recurring BOOLEAN DEFAULT 0
            )
            """
        )
        self.conn.commit()

    def add_event(self, event: CalendarEvent) -> None:
        with self.conn:
            self.cursor.execute(
                f"""
                INSERT INTO {self.database_name} (date, time, description, color, is_recurring)
                VALUES (?, ?, ?, ?, ?)
                """, (pickle.dumps(event.date), pickle.dumps(event.time), event.description, event.color,
                      int(event.is_recurring))
            )
            self.conn.commit()

    def get_events_for_date(self, date: datetime.date) -> list[CalendarEvent]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT date, time, description, color, is_recurring
                FROM {self.database_name}
                WHERE date = ?
                """,
                (pickle.dumps(date), )
            )
            return list(
                map(lambda t: CalendarEvent(pickle.loads(t[1]), pickle.loads(t[2]), t[3], t[4], t[5]),
                    self.cursor.fetchall())
            )

    def remove_event(self, event: CalendarEvent) -> None:
        with self.conn:
            self.cursor.execute(f"""DELETE from {self.database_name} 
                                WHERE date = :date AND time = :time AND description = :description""",
                                {"date": pickle.dumps(event.date),
                                 "time": pickle.dumps(event.time), "description": event.description})




