import datetime
import inspect
import time
from threading import Thread

import pytz as pytz
from googleapiclient.discovery import Resource

from src.events.event import CalendarSyncEvent
from src.events.event_loop import EventLoop
from src.main.account_manager import AccountManager
from src.models.calendar_model import CalendarModel, CalendarEvent, EventRecurring
from src.ui.colors import Colors, Color
from src.utils.authentication import GoogleAuthentication
from src.utils.singleton import Singleton


class CalendarSyncManager(metaclass=Singleton):

    def __init__(self, model: CalendarModel = None, event_loop: EventLoop = None) -> None:
        self.model = model
        self.event_loop = event_loop

    def fetch_events(self, dt: datetime.datetime) -> (Resource, list[dict]):
        if not AccountManager().current_account:
            return []

        service = GoogleAuthentication.initialize_service(AccountManager().current_account.email)

        now = dt.isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now
        ).execute()

        events = events_result.get("items", [])

        return service, events

    def sync_calendars(self) -> None:
        now = datetime.datetime.utcnow()

        service, google_events = self.fetch_events(now)
        google_calendar_events = []
        local_calendar_events = self.model.get_upcoming_events(now, threaded=True)

        add_to_local = []
        for event in google_events:
            description = ""
            if "summary" in event:
                description = event["summary"]
            elif "description" in event:
                description = event["description"]
            color_id = "0"
            if "colorId" in event:
                color_id = event["colorId"]
            color = self.get_color_by_id(color_id)
            if "date" in event["start"]:
                date = datetime.datetime.fromisoformat(event["start"]["date"])
            else:
                date = datetime.datetime.fromisoformat(event["start"]["dateTime"].rstrip("Z"))
                time_zone = event["start"]["timeZone"]

                if time_zone.upper() != "UTC":
                    tz = pytz.timezone(time_zone)
                    date = tz.localize(date).astimezone(pytz.utc)

            recurrence = EventRecurring.NEVER
            if "recurrence" in event:
                if event["recurrence"][0] == "RRULE:FREQ=MONTHLY":
                    recurrence = EventRecurring.MONTHLY
                elif event["recurrence"][0] == "RRULE:FREQ=YEARLY":
                    recurrence = EventRecurring.YEARLY
                elif "RRULE:FREQ=WEEKLY;BYDAY" in event["recurrence"][0]:
                    recurrence = EventRecurring.WEEKLY

            calendar_event = CalendarEvent(date.date(), date.time(), description, color, recurrence, 0)
            google_calendar_events.append(calendar_event)

            for local_event in local_calendar_events:
                if self.model.compare_events(local_event, calendar_event):
                    break
            else:
                add_to_local.append(calendar_event)

        add_to_google = []
        for event in local_calendar_events:
            for google_event in google_calendar_events:
                if self.model.compare_events(event, google_event):
                    break
            else:
                add_to_google.append(event)

        for event in add_to_google:
            self.add_event_to_google(service, event)

        for event in add_to_local:
            self.model.add_event(event, threaded=True)

    def sync_calendars_threaded(self) -> None:
        def sync(on_complete):
            CalendarSyncManager().sync_calendars()
            on_complete()

        def callback():
            self.event_loop.enqueue_threaded_event(CalendarSyncEvent(time.time()))

        Thread(target=sync, args=(callback, )).start()

    def add_event_to_google(self, service: Resource, event: CalendarEvent) -> None:
        summary = event.description
        dt = event.date.strftime("%Y-%m-%d") + "T" + event.time.strftime("%H:%M") + ":00Z"

        google_event = {
            "summary": summary,
            "start": {
                "dateTime": dt,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": dt,
                "timeZone": "UTC"
            }
        }

        if event.recurring is EventRecurring.WEEKLY:
            day = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"][datetime.datetime.fromisoformat(dt.rstrip("Z")).weekday()]
            google_event["recurrence"] = ["RRULE:FREQ=WEEKLY;BYDAY=" + day]
        elif event.recurring is EventRecurring.MONTHLY:
            google_event["recurrence"] = ["RRULE:FREQ=MONTHLY"]
        elif event.recurring is EventRecurring.YEARLY:
            google_event["recurrence"] = ["RRULE:FREQ=YEARLY"]

        service.events().insert(calendarId="primary", body=google_event).execute()

    @staticmethod
    def get_color_by_id(color_id: str) -> Color:
        colors = [Colors.EVENT_BLUE204, Colors.EVENT_PINK204, Colors.EVENT_GREEN204, Colors.EVENT_PURPLE204,
                  Colors.EVENT_RED204, Colors.EVENT_YELLOW204, Colors.EVENT_ORANGE, None, None,
                  Colors.EVENT_BLUE, Colors.EVENT_GREEN, Colors.EVENT_RED]
        return colors[int(color_id)]
