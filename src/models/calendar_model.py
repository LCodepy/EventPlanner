import datetime
import os
import pickle
import sqlite3
from dataclasses import dataclass

from src.ui.colors import Color, Colors, get_rgb_color, get_hex_color
from src.utils.assets import Assets


@dataclass
class CalendarEvent:

    date: datetime.date
    time: datetime.time
    description: str
    color: Color
    is_recurring: bool


class CalendarModel:

    def __init__(self) -> None:
        self.database_name = "calendar"
        self.calendar_exists = False

        if os.path.exists(Assets().calendar_database_path):
            self.calendar_exists = True

        self.conn = sqlite3.connect(Assets().calendar_database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.database_name} (
                year INTEGER,
                month INTEGER,
                day INTEGER,
                hour INTEGER,
                minute INTEGER,
                second INTEGER,
                description TEXT,
                color TEXT,
                is_recurring BOOLEAN DEFAULT 0
            )
            """
        )
        self.conn.commit()

        self.default_events = []
        self.add_default_events()

    def add_default_events(self) -> None:
        if self.calendar_exists:
            return

        for event in self.default_events:
            self.add_event(event)

    def add_event(self, event: CalendarEvent) -> None:
        with self.conn:
            self.cursor.execute(
                f"""
                INSERT INTO {self.database_name} (year, month, day, hour, minute, second, description, color, is_recurring)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (event.date.year, event.date.month, event.date.day, event.time.hour, event.time.minute,
                      int(event.time.second), event.description, get_hex_color(event.color), int(event.is_recurring))
            )
            self.conn.commit()

    def get_events_for_date(self, date: datetime.date) -> list[CalendarEvent]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT year, month, day, hour, minute, second, description, color, is_recurring
                FROM {self.database_name}
                WHERE year = ? AND month = ? AND day = ?
                """,
                (date.year, date.month, date.day)
            )
            return list(
                map(
                    lambda t: CalendarEvent(
                        datetime.date(t[0], t[1], t[2]), datetime.time(t[3], t[4], t[5]), t[6], get_rgb_color(t[7]), t[8]
                    ),
                    self.cursor.fetchall()
                )
            )

    def get_events_for_month(self, year: int, month: int) -> list[list[CalendarEvent]]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT year, month, day, hour, minute, second, description, color, is_recurring
                FROM {self.database_name}
                WHERE year = ? AND month = ?
                """,
                (year, month)
            )
            events = list(
                map(
                    lambda t: CalendarEvent(
                        datetime.date(t[0], t[1], t[2]), datetime.time(t[3], t[4], t[5]), t[6], get_rgb_color(t[7]), t[8]
                    ),
                    self.cursor.fetchall()
                )
            )
            ret = [[] for _ in range(31)]
            for event in events:
                ret[event.date.day-1].append(event)
            return ret

    def remove_event(self, event: CalendarEvent) -> None:
        with self.conn:
            self.cursor.execute(f"""DELETE from {self.database_name} 
                                WHERE year = :year AND month = :month AND day = :day AND hour = :hour AND minute = :minute AND description = :description AND color = :color""",
                                {"year": event.date.year, "month": event.date.month, "day": event.date.day, "hour": event.time.hour,
                                 "minute": event.time.minute, "description": event.description, "color": get_hex_color(event.color)})

    def update_event(self, event: CalendarEvent, t: datetime.time = None, description: str = None, color: Color = None, is_recurring: bool = None):
        new_event = CalendarEvent(event.date, t or event.time, description or event.description, color or event.color, is_recurring or event.is_recurring)
        with self.conn:
            self.cursor.execute(f"""
                UPDATE {self.database_name} SET hour = ?, minute = ?, description = ?, color = ?, is_recurring = ?
                WHERE year = ? AND month = ? AND day = ? AND hour = ? AND minute = ? AND description = ? AND color = ?
            """, (new_event.time.hour, new_event.time.minute, new_event.description, get_hex_color(new_event.color),
                  new_event.is_recurring, event.date.year, event.date.month, event.date.day, event.time.hour,
                  event.time.minute, event.description, get_hex_color(event.color)))


