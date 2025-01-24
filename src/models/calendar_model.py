import datetime
import os
import pickle
import sqlite3
from dataclasses import dataclass
from enum import Enum, auto

from src.main.settings import Settings
from src.ui.colors import Color, get_rgb_color, get_hex_color
from src.utils.assets import Assets
from src.utils.calendar_functions import get_month_length, calculate_easter
from src.main.language_manager import LanguageManager


class EventRecurrence(Enum):
    NEVER = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    YEARLY = auto()


@dataclass
class CalendarEvent:
    id: int
    date: datetime.date
    time: datetime.time
    description: str
    color: Color
    recurrence: EventRecurrence
    is_default: bool = False
    google_id: str = ""


class CalendarModel:

    def __init__(self, database_name: str = "calendar") -> None:
        self.database_name = database_name
        
        self.calendar_database_path = os.path.join(Assets().calendar_database_path, database_name + ".db")

        self.conn = sqlite3.connect(self.calendar_database_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS "{self.database_name}" (
                id INTEGER,
                year INTEGER,
                month INTEGER,
                day INTEGER,
                hour INTEGER,
                minute INTEGER,
                second INTEGER,
                description TEXT,
                color TEXT,
                recurrence BLOB,
                is_default INTEGER,
                google_id TEXT
            )
            """
        )
        self.conn.commit()

        self.current_id = None
        self.load_current_id()

        self.default_event_color = None
        self.catholic_event_color = None
        self.load_data()

    def load_data(self) -> None:
        settings = Settings().get_settings()

        self.default_event_color = get_rgb_color(settings["default_event_color"])
        self.catholic_event_color = get_rgb_color(settings["catholic_event_color"])

    def load_current_id(self) -> None:
        settings = Settings().get_settings()

        if self.database_name not in settings["current_id"]:
            settings["current_id"][self.database_name] = 0
            Settings().save_settings(settings)

        self.current_id = settings["current_id"][self.database_name]

    def add_event(self, event: CalendarEvent, threaded: bool = False) -> None:
        self.load_current_id()

        if threaded:
            conn = sqlite3.connect(self.calendar_database_path)
            cursor = conn.cursor()
        else:
            conn = self.conn
            cursor = self.cursor

        with conn:
            cursor.execute(
                f"""
                INSERT INTO "{self.database_name}" (id, year, month, day, hour, minute, second, description, color, 
                recurrence, is_default, google_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.current_id, event.date.year, event.date.month, event.date.day, event.time.hour,
                      event.time.minute, int(event.time.second), event.description, get_hex_color(event.color),
                      pickle.dumps(event.recurrence), event.is_default, event.google_id)
            )
            conn.commit()

        self.current_id += 1

        Settings().update_settings(["current_id", self.database_name], self.current_id)

    def get_events_for_date(self, date: datetime.date) -> list[CalendarEvent]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT id, year, month, day, hour, minute, second, description, color, recurrence, is_default, google_id
                FROM "{self.database_name}"
                WHERE year = ? AND month = ? AND day = ? AND recurrence = ?
                """,
                (date.year, date.month, date.day, pickle.dumps(EventRecurrence.NEVER))
            )

        default_events = list(filter(lambda ev: ev.date == date, self.get_default_events()))
        easter_events = list(filter(lambda ev: ev.date == date, self.get_easter_events(date.year)))
        catholic_events = list(filter(lambda ev: ev.date.month == date.month and ev.date.day == date.day,
                                      self.get_catholic_events()))

        return default_events + easter_events + catholic_events + list(
            map(
                lambda t: CalendarEvent(
                    t[0], datetime.date(t[1], t[2], t[3]), datetime.time(t[4], t[5], t[6]), t[7], get_rgb_color(t[8]),
                    pickle.loads(t[9]), t[10], t[11]
                ),
                self.cursor.fetchall()
            )
        ) + self.get_recurring_events(date.year, date.month, date.day)

    def get_events_for_month(self, year: int, month: int) -> list[list[CalendarEvent]]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT id, year, month, day, hour, minute, second, description, color, recurrence, is_default, google_id
                FROM "{self.database_name}"
                WHERE year = ? AND month = ? AND recurrence = ?
                """,
                (year, month, pickle.dumps(EventRecurrence.NEVER),)
            )

            events = list(
                map(
                    lambda t: CalendarEvent(
                        t[0], datetime.date(t[1], t[2], t[3]), datetime.time(t[4], t[5], t[6]), t[7],
                        get_rgb_color(t[8]),
                        pickle.loads(t[9]), t[10], t[11]
                    ),
                    self.cursor.fetchall()
                )
            )

        default_events = list(filter(lambda ev: ev.date.month == month, self.get_default_events()))
        easter_events = list(filter(lambda ev: ev.date.month == month, self.get_easter_events(year)))
        catholic_events = list(filter(lambda ev: ev.date.month == month, self.get_catholic_events()))

        recurring_events = self.get_recurring_events(year, month)

        ret = [[] for _ in range(get_month_length(month))]

        for event in default_events + easter_events + catholic_events + events + recurring_events:
            ret[event.date.day - 1].append(event)

        return ret

    def get_recurring_events(self, year: int, month: int, day: int = None) -> list[CalendarEvent]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT id, year, month, day, hour, minute, second, description, color, recurrence, is_default, google_id
                FROM "{self.database_name}"
                WHERE recurrence != ?
                """,
                (pickle.dumps(EventRecurrence.NEVER),)
            )

            events = list(
                map(
                    lambda t: CalendarEvent(
                        t[0], datetime.date(t[1], t[2], t[3]), datetime.time(t[4], t[5], t[6]), t[7],
                        get_rgb_color(t[8]),
                        pickle.loads(t[9]), t[10], t[11]
                    ),
                    self.cursor.fetchall()
                )
            )

        ret = []
        for event in events:
            if event.recurrence == EventRecurrence.WEEKLY:
                for i in range(get_month_length(month)):
                    if day and day != i + 1:
                        continue
                    if datetime.date(year, month, i + 1).weekday() == event.date.weekday():
                        ret.append(
                            CalendarEvent(
                                event.id, datetime.date(year, month, i + 1), event.time,
                                event.description, event.color, event.recurrence, event.is_default, event.google_id
                            )
                        )
            elif (
                    event.recurrence == EventRecurrence.MONTHLY and
                    event.date.day <= get_month_length(month) and
                    (not day or event.date.day == day)
            ):
                ret.append(
                    CalendarEvent(
                        event.id, datetime.date(year, month, event.date.day), event.time,
                        event.description, event.color, event.recurrence, event.is_default, event.google_id
                    )
                )
            elif event.recurrence == EventRecurrence.YEARLY and event.date.month == month and (
                    not day or event.date.day == day):
                ret.append(
                    CalendarEvent(
                        event.id, datetime.date(year, month, event.date.day), event.time,
                        event.description, event.color, event.recurrence, event.is_default, event.google_id
                    )
                )

        return ret

    def get_default_events(self) -> list[CalendarEvent]:
        events = LanguageManager().get_string("default_event_list")
        default_events = []

        for i, event in enumerate(events):
            if not event["date"]:
                continue
            month, day = event["date"].split("-")
            date = datetime.date(datetime.datetime.now().year, int(month), int(day))

            default_events.append(
                CalendarEvent(
                    i, date, datetime.time(0, 0), event["description"],
                    self.default_event_color, EventRecurrence.YEARLY, is_default=True
                )
            )

        self.current_id = max(self.current_id, len(default_events))
        return default_events

    def get_easter_events(self, year: int) -> list[CalendarEvent]:
        easter = datetime.date(*calculate_easter(year))
        easter_m = easter + datetime.timedelta(days=1)
        tijelovo = easter + datetime.timedelta(days=60)

        easter_events = [
            CalendarEvent(
                -1, easter, datetime.time(0, 0), "Uskrs", self.default_event_color, EventRecurrence.NEVER,
                is_default=True
            ),
            CalendarEvent(
                -2, easter_m, datetime.time(0, 0), "Uskršnji ponedjeljak", self.default_event_color,
                EventRecurrence.NEVER, is_default=True
            ),
            CalendarEvent(
                -3, tijelovo, datetime.time(0, 0), "Tijelovo", self.default_event_color, EventRecurrence.NEVER,
                is_default=True
            )
        ]

        return easter_events

    def get_catholic_events(self) -> list[CalendarEvent]:
        settings = Settings().get_settings()
        catholic_events = LanguageManager().get_string("catholic_event_list")

        if not settings["show_catholic_events"]:
            return []

        events = []
        for i, event in enumerate(catholic_events):
            if not event["date"]:
                continue
            month, day = event["date"].split("-")
            date = datetime.date(datetime.datetime.now().year, int(month), int(day))

            events.append(
                CalendarEvent(
                    -(i + 100), date, datetime.time(0, 0), event["description"],
                    self.catholic_event_color, EventRecurrence.NEVER, is_default=True
                )
            )

        return events

    def get_upcoming_events(self, date: datetime.datetime, threaded: bool = False) -> list[CalendarEvent]:
        if threaded:
            conn = sqlite3.connect(self.calendar_database_path)
            cursor = conn.cursor()
        else:
            conn = self.conn
            cursor = self.cursor

        with conn:
            cursor.execute(
                f"""
                SELECT id, year, month, day, hour, minute, second, description, color, recurrence, is_default, google_id
                FROM "{self.database_name}"
                WHERE recurrence != ? OR year > ? OR (year = ? AND month > ?) OR (year = ? AND month = ? AND day >= ?)
                """,
                (pickle.dumps(EventRecurrence.NEVER), date.year, date.year, date.month, date.year, date.month, date.day)
            )

            events = list(
                map(
                    lambda t: CalendarEvent(
                        t[0], datetime.date(t[1], t[2], t[3]), datetime.time(t[4], t[5], t[6]), t[7],
                        get_rgb_color(t[8]),
                        pickle.loads(t[9]), t[10], t[11]
                    ),
                    cursor.fetchall()
                )
            )
            events = list(
                filter(
                    lambda e: e.date != date.date() or (e.time.hour > date.hour or (e.time.hour <= date.hour and e.time.minute > date.minute)),
                    events
                )
            )

        return events

    def remove_event(self, event: CalendarEvent, threaded: bool = False) -> None:
        if threaded:
            conn = sqlite3.connect(self.calendar_database_path)
            cursor = conn.cursor()
        else:
            conn = self.conn
            cursor = self.cursor

        with conn:
            cursor.execute(f"""DELETE from "{self.database_name}" WHERE id = :id""", {"id": event.id})
            # self.cursor.execute(f"""DELETE from {self.database_name}
            #                     WHERE year = :year AND month = :month AND day = :day AND hour = :hour AND
            #                     minute = :minute AND description = :description AND color = :color AND
            #                     recurring = :recurring AND recurrence_id = :recurrence_id""",
            #                     {"year": event.date.year, "month": event.date.month, "day": event.date.day,
            #                      "hour": event.time.hour,
            #                      "minute": event.time.minute, "description": event.description,
            #                      "color": get_hex_color(event.color), "recurring": pickle.dumps(event.recurrence),
            #                      "recurrence_id": event.recurrence_id})

    def update_event(self, event: CalendarEvent, updated_event: CalendarEvent = None, d: datetime.date = None,
                     t: datetime.time = None, description: str = None, color: Color = None,
                     recurrence: EventRecurrence = None, google_id: str = None,
                     threaded: bool = False) -> None:
        new_event = updated_event or CalendarEvent(
            event.id, d or event.date, t or event.time, description or event.description, color or event.color,
            recurrence or event.recurrence, google_id=google_id or event.google_id
        )

        if threaded:
            conn = sqlite3.connect(self.calendar_database_path)
            cursor = conn.cursor()
        else:
            conn = self.conn
            cursor = self.cursor

        with conn:
            cursor.execute(
                f"""
                UPDATE "{self.database_name}" SET year = ?, month = ?, day = ?, hour = ?, minute = ?, description = ?, 
                color = ?, recurrence = ?, google_id = ? WHERE id = ?
                """,
                (new_event.date.year, new_event.date.month, new_event.date.day, new_event.time.hour,
                 new_event.time.minute, new_event.description, get_hex_color(new_event.color),
                 pickle.dumps(new_event.recurrence), new_event.google_id, event.id)
            )

    def search_events(self, query: str) -> list[CalendarEvent]:
        with self.conn:
            self.cursor.execute(
                f"""
                SELECT id, year, month, day, hour, minute, second, description, color, recurrence, is_default, google_id
                FROM "{self.database_name}"
                WHERE description LIKE ?
                """,
                (f"%{query}%",)
            )

            default_events = list(
                filter(lambda ev: query.lower() in ev.description.lower(), self.get_default_events())
            )

            easter_events = list(
                filter(lambda ev: query.lower() in ev.description.lower(),
                       self.get_easter_events(datetime.datetime.now().year))
            )
            catholic_events = list(
                filter(lambda ev: query.lower() in ev.description.lower(), self.get_catholic_events())
            )

            return default_events + easter_events + catholic_events + list(
                map(
                    lambda t: CalendarEvent(
                        t[0], datetime.date(t[1], t[2], t[3]), datetime.time(t[4], t[5], t[6]), t[7],
                        get_rgb_color(t[8]),
                        pickle.loads(t[9]), t[10], t[11]
                    ),
                    self.cursor.fetchall()
                )
            )

    def compare_events(self, event1: CalendarEvent, event2: CalendarEvent) -> bool:
        return (
                event1.description == event2.description and event1.date == event2.date and
                event1.time == event2.time and event1.recurrence == event2.recurrence and event1.color == event2.color
        )
