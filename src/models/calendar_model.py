import datetime
import os
import pickle
import sqlite3
from dataclasses import dataclass
from enum import Enum, auto

from src.ui.colors import Color, Colors, get_rgb_color, get_hex_color
from src.utils.assets import Assets
from src.utils.calendar_functions import get_month_length


class EventRecurring(Enum):
    NEVER = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    YEARLY = auto()


@dataclass
class CalendarEvent:

    date: datetime.date
    time: datetime.time
    description: str
    color: Color
    recurring: EventRecurring
    recurrence_id: int


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
                recurring BLOB,
                recurrence_id INTEGER
            )
            """
        )
        self.conn.commit()

        self.current_recurring_id = 0

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
                INSERT INTO {self.database_name} (year, month, day, hour, minute, second, description, color, recurring,
                recurrence_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (event.date.year, event.date.month, event.date.day, event.time.hour, event.time.minute,
                      int(event.time.second), event.description, get_hex_color(event.color),
                      pickle.dumps(event.recurring), self.current_recurring_id)
            )
            self.conn.commit()
            self.current_recurring_id += 1

    def get_events_for_date(self, date: datetime.date) -> list[CalendarEvent]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT year, month, day, hour, minute, second, description, color, recurring, recurrence_id
                FROM {self.database_name}
                WHERE year = ? AND month = ? AND day = ? AND recurring = ?
                """,
                (date.year, date.month, date.day, pickle.dumps(EventRecurring.NEVER))
            )
        return list(
            map(
                lambda t: CalendarEvent(
                    datetime.date(t[0], t[1], t[2]), datetime.time(t[3], t[4], t[5]), t[6], get_rgb_color(t[7]),
                    pickle.loads(t[8]), t[9]
                ),
                self.cursor.fetchall()
            )
        ) + self.get_recurring_events(date.year, date.month, date.day)

    def get_events_for_month(self, year: int, month: int) -> list[list[CalendarEvent]]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT year, month, day, hour, minute, second, description, color, recurring, recurrence_id
                FROM {self.database_name}
                WHERE year = ? AND month = ? AND recurring = ?
                """,
                (year, month, pickle.dumps(EventRecurring.NEVER), )
            )

            events = list(
                map(
                    lambda t: CalendarEvent(
                        datetime.date(t[0], t[1], t[2]), datetime.time(t[3], t[4], t[5]), t[6], get_rgb_color(t[7]),
                        pickle.loads(t[8]), t[9]
                    ),
                    self.cursor.fetchall()
                )
            )

        recurring_events = self.get_recurring_events(year, month)

        ret = [[] for _ in range(get_month_length(month))]

        for event in events:
            ret[event.date.day - 1].append(event)

        for event in recurring_events:
            ret[event.date.day - 1].append(event)

        return ret

    def get_recurring_events(self, year: int, month: int, day: int = None) -> list[CalendarEvent]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT year, month, day, hour, minute, second, description, color, recurring, recurrence_id
                FROM {self.database_name}
                WHERE recurring != ?
                """,
                (pickle.dumps(EventRecurring.NEVER),)
            )

            events = list(
                map(
                    lambda t: CalendarEvent(
                        datetime.date(t[0], t[1], t[2]), datetime.time(t[3], t[4], t[5]), t[6], get_rgb_color(t[7]),
                        pickle.loads(t[8]), t[9]
                    ),
                    self.cursor.fetchall()
                )
            )

        ret = []
        for event in events:
            if event.recurring == EventRecurring.WEEKLY:
                for i in range(get_month_length(month)):
                    if day and day != i + 1:
                        continue
                    if datetime.date(year, month, i + 1).weekday() == event.date.weekday():
                        ret.append(
                            CalendarEvent(
                                datetime.date(year, month, i + 1), event.time,
                                event.description, event.color, event.recurring, event.recurrence_id
                            )
                        )
            elif (
                    event.recurring == EventRecurring.MONTHLY and
                    event.date.day <= get_month_length(month) and
                    (not day or event.date.day == day)
            ):
                ret.append(
                    CalendarEvent(
                        datetime.date(year, month, event.date.day), event.time,
                        event.description, event.color, event.recurring, event.recurrence_id
                    )
                )
            elif event.recurring == EventRecurring.YEARLY and event.date.month == month and (
                    not day or event.date.day == day):
                ret.append(
                    CalendarEvent(
                        datetime.date(year, month, event.date.day), event.time,
                        event.description, event.color, event.recurring, event.recurrence_id
                    )
                )

        return ret

    def remove_event(self, event: CalendarEvent) -> None:
        with self.conn:
            if event.recurring is not EventRecurring.NEVER:
                self.cursor.execute(f"""DELETE from {self.database_name} 
                                    WHERE recurrence_id = :recurrence_id""",
                                    {"recurrence_id": event.recurrence_id})
            else:
                self.cursor.execute(f"""DELETE from {self.database_name} 
                                    WHERE year = :year AND month = :month AND day = :day AND hour = :hour AND 
                                    minute = :minute AND description = :description AND color = :color AND
                                    recurring = :recurring AND recurrence_id = :recurrence_id""",
                                    {"year": event.date.year, "month": event.date.month, "day": event.date.day,
                                     "hour": event.time.hour,
                                     "minute": event.time.minute, "description": event.description,
                                     "color": get_hex_color(event.color), "recurring": pickle.dumps(event.recurring),
                                     "recurrence_id": event.recurrence_id})

    def update_event(self, event: CalendarEvent, d: datetime.date = None, t: datetime.time = None, description: str = None, color: Color = None,
                     recurring: EventRecurring = EventRecurring.NEVER):
        date = d if event.recurring is not EventRecurring.NEVER else event.date
        new_event = CalendarEvent(date, t or event.time, description or event.description, color or event.color,
                                  recurring or event.recurring, 0)
        with self.conn:
            self.cursor.execute(f"""
                UPDATE {self.database_name} SET year = ?, month = ?, day = ?, hour = ?, minute = ?, description = ?, 
                color = ?, recurring = ? WHERE recurrence_id = ?""",
                                (new_event.date.year, new_event.date.month, new_event.date.day, new_event.time.hour,
                                 new_event.time.minute, new_event.description, get_hex_color(new_event.color),
                                 pickle.dumps(new_event.recurring), event.recurrence_id)
                                )
