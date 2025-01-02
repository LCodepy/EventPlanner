import datetime
import json
import os
import pickle
import sqlite3
from dataclasses import dataclass
from enum import Enum, auto

from src.ui.colors import Color, Colors, get_rgb_color, get_hex_color
from src.utils.assets import Assets
from src.utils.calendar_functions import get_month_length, calculate_easter


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

        self.current_recurring_id = None
        self.load_recurring_id()

        self.default_events = []
        self.default_event_color = None
        self.catholic_event_color = None
        self.load_default_events()
        self.add_default_events()

    def load_default_events(self) -> None:
        with open(Assets().settings_database_path, "r", encoding="utf-16") as file:
            fjson = json.load(file)

            self.default_event_color = fjson["default_event_color"]
            self.catholic_event_color = fjson["catholic_event_color"]

            for i, event in enumerate(fjson["default_events"]):
                if not event["date"]:
                    continue
                month, day = event["date"].split("-")
                date = datetime.date(datetime.datetime.now().year, int(month), int(day))

                self.default_events.append(
                    CalendarEvent(
                        date, datetime.time(0, 0), event["description"], get_rgb_color(self.default_event_color),
                        EventRecurring.YEARLY, -(i + 4)
                    )
                )

    def load_recurring_id(self) -> None:
        with open(Assets().settings_database_path, "r", encoding="utf-16") as file:
            self.current_recurring_id = json.load(file)["current_recurring_id"]

    def add_default_events(self) -> None:
        if self.calendar_exists:
            return

        for event in self.default_events:
            self.add_event(event, default_event=True)

    def add_event(self, event: CalendarEvent, default_event: bool = False, threaded: bool = False) -> None:
        current_recurring_id = event.recurrence_id if default_event else self.current_recurring_id

        if threaded:
            conn = sqlite3.connect(Assets().calendar_database_path)
            cursor = conn.cursor()
        else:
            conn = self.conn
            cursor = self.cursor

        with conn:
            cursor.execute(
                f"""
                INSERT INTO {self.database_name} (year, month, day, hour, minute, second, description, color, recurring,
                recurrence_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (event.date.year, event.date.month, event.date.day, event.time.hour, event.time.minute,
                      int(event.time.second), event.description, get_hex_color(event.color),
                      pickle.dumps(event.recurring), current_recurring_id)
            )
            conn.commit()

        if default_event:
            return

        self.current_recurring_id += 1

        with open(Assets().settings_database_path, "r", encoding="utf-16") as file:
            data = json.load(file)

        data["current_recurring_id"] = self.current_recurring_id

        with open(Assets().settings_database_path, "w", encoding="utf-16") as file:
            json.dump(data, file)

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

        easter_events = list(filter(lambda ev: ev.date == date, self.get_easter_events(date.year)))
        catholic_events = list(filter(lambda ev: ev.date.month == date.month and ev.date.day == date.day,
                                      self.get_catholic_events()))

        return easter_events + catholic_events + list(
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

        easter_events = list(filter(lambda ev: ev.date.month == month, self.get_easter_events(year)))
        catholic_events = list(filter(lambda ev: ev.date.month == month, self.get_catholic_events()))

        recurring_events = self.get_recurring_events(year, month)

        ret = [[] for _ in range(get_month_length(month))]

        for event in easter_events + catholic_events + events + recurring_events:
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

    def get_easter_events(self, year: int) -> list[CalendarEvent]:
        easter = datetime.date(*calculate_easter(year))
        easter_m = easter + datetime.timedelta(days=1)
        tijelovo = easter + datetime.timedelta(days=60)

        easter_events = [
            CalendarEvent(
                easter, datetime.time(0, 0), "Uskrs", self.default_event_color, EventRecurring.NEVER, -1
            ),
            CalendarEvent(
                easter_m, datetime.time(0, 0), "Uskršnji ponedjeljak", self.default_event_color,
                EventRecurring.NEVER, -2
            ),
            CalendarEvent(
                tijelovo, datetime.time(0, 0), "Tijelovo", self.default_event_color, EventRecurring.NEVER, -3
            )
        ]

        return easter_events

    def get_catholic_events(self) -> list[CalendarEvent]:
        with open(Assets().settings_database_path, "r", encoding="utf-16") as file:
            fjson = json.load(file)

            if not fjson["show_catholic_events"]:
                return []

            events = []
            for i, event in enumerate(fjson["catholic_events"]):
                if not event["date"]:
                    continue
                month, day = event["date"].split("-")
                date = datetime.date(datetime.datetime.now().year, int(month), int(day))

                events.append(
                    CalendarEvent(
                        date, datetime.time(0, 0), event["description"], get_rgb_color(self.catholic_event_color),
                        EventRecurring.NEVER, -(i + 100)
                    )
                )

            return events

    def get_upcoming_events(self, date: datetime.date, threaded: bool = False) -> list[CalendarEvent]:
        if threaded:
            conn = sqlite3.connect(Assets().calendar_database_path)
            cursor = conn.cursor()
        else:
            conn = self.conn
            cursor = self.cursor

        with conn:
            cursor.execute(
                f"""
                SELECT year, month, day, hour, minute, second, description, color, recurring, recurrence_id
                FROM {self.database_name}
                WHERE (recurring != ? OR year > ? OR (year = ? AND month > ?) OR (year = ? AND month = ? AND day >= ?))
                AND recurrence_id >= ?
                """,
                (pickle.dumps(EventRecurring.NEVER), date.year, date.year, date.month, date.year, date.month, date.day, 0)
            )

            events = list(
                map(
                    lambda t: CalendarEvent(
                        datetime.date(t[0], t[1], t[2]), datetime.time(t[3], t[4], t[5]), t[6], get_rgb_color(t[7]),
                        pickle.loads(t[8]), t[9]
                    ),
                    cursor.fetchall()
                )
            )

        return events

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

    def update_event(self, event: CalendarEvent, d: datetime.date = None, t: datetime.time = None,
                     description: str = None, color: Color = None, recurring: EventRecurring = EventRecurring.NEVER):
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

    def search_events(self, query: str) -> list[CalendarEvent]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT year, month, day, hour, minute, second, description, color, recurring, recurrence_id
                FROM {self.database_name}
                WHERE description LIKE ?
                """,
                (f"%{query}%",)
            )

            catholic_events = list(filter(lambda ev: query.lower() in ev.description.lower(), self.get_catholic_events()))

            return catholic_events + list(
                map(
                    lambda t: CalendarEvent(
                        datetime.date(t[0], t[1], t[2]), datetime.time(t[3], t[4], t[5]), t[6], get_rgb_color(t[7]),
                        pickle.loads(t[8]), t[9]
                    ),
                    self.cursor.fetchall()
                )
            )

    def compare_events(self, event1: CalendarEvent, event2: CalendarEvent) -> bool:
        return(
            event1.description == event2.description and event1.date == event2.date and
            event1.time == event2.time and event1.recurring == event2.recurring
        )
