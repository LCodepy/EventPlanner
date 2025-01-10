import datetime
import inspect
import time
from threading import Thread

import pytz as pytz
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from httplib2 import ServerNotFoundError

from src.events.event import CalendarSyncEvent, Event, UserSignInEvent, EditCalendarEventEvent, \
    DeleteCalendarEventEvent, UserSignOutEvent
from src.events.event_loop import EventLoop
from src.main.account_manager import AccountManager
from src.main.config import Config
from src.models.calendar_model import CalendarModel, CalendarEvent, EventRecurrence
from src.ui.colors import Colors, Color
from src.utils.authentication import GoogleAuthentication
from src.utils.singleton import Singleton


class CalendarSyncManager(metaclass=Singleton):

    def __init__(self, event_loop: EventLoop = None) -> None:
        self.event_loop = event_loop

        if AccountManager().current_account is not None:
            self.model = CalendarModel(
                database_name=f"calendar_{AccountManager().current_account.email}"
            )
        else:
            self.model = CalendarModel()

        self.events_to_delete = {user.email: [] for user in AccountManager().accounts}
        self.events_to_edit = {user.email: [] for user in AccountManager().accounts}

        self.sync_finished = True
        self.last_synced = 0
        self.sync_time = 6

    def register_event(self, event: Event) -> None:
        if isinstance(event, UserSignInEvent):
            if event.user.email not in self.events_to_delete:
                self.events_to_delete[event.user.email] = []
                self.events_to_edit[event.user.email] = []

            self.model = CalendarModel(
                database_name=f"calendar_{AccountManager().current_account.email}"
            )
        elif isinstance(event, UserSignOutEvent):
            self.model = CalendarModel()
        elif isinstance(event, EditCalendarEventEvent):
            self.update_event(
                event.event, d=event.event.date, t=event.time, description=event.description,
                color=event.color, recurrence=event.recurrence
            )
        elif isinstance(event, DeleteCalendarEventEvent):
            self.remove_event(event.event)
            print("DELETED")
        elif isinstance(event, CalendarSyncEvent):
            self.sync_finished = True

        if time.time() - self.last_synced > self.sync_time and self.sync_finished:
            self.last_synced = time.time()
            # self.sync_calendars_threaded()
            self.sync_all_calendars_threaded()

    def fetch_events(self, dt: datetime.datetime, email: str = None) -> (Resource, list[dict]):
        if not AccountManager().current_account:
            return []

        service = GoogleAuthentication.initialize_service(email or AccountManager().current_account.email)

        now = dt.isoformat() + "Z"

        try:
            events_result = service.events().list(
                calendarId="primary",
                timeMin=now
            ).execute()
        except ServerNotFoundError as e:
            print(e)
            return None, None

        events = events_result.get("items", [])

        return service, events

    def sync_calendars(self, email: str = None) -> None:
        if not AccountManager().is_signed_in():
            return

        now = datetime.datetime.utcnow()

        service, _ = self.fetch_events(now, email=email)

        if not service:
            return

        self.sync_finished = False

        self.sync_deleted_events(service, email=email)
        self.sync_updated_events(service, email=email)

        service, google_events = self.fetch_events(now, email=email)

        if email:
            model = CalendarModel(database_name=f"calendar_{email}")
        else:
            model = self.model

        google_calendar_events = self.get_google_event_list(google_events)
        local_calendar_events = model.get_upcoming_events(now, threaded=True)

        local_synced = {}
        local_not_synced = []
        for event in local_calendar_events:
            if event.google_id:
                local_synced[event.google_id] = event
            else:
                local_not_synced.append(event)

        google_synced = {}
        google_not_synced = []
        for event in google_calendar_events:
            if event.google_id in local_synced.keys():
                google_synced[event.google_id] = event
            else:
                google_not_synced.append(event)

        for event in local_not_synced:
            google_id = self.add_event_to_google(service, event)
            self.model.update_event(event, google_id=google_id, threaded=True)

        for event in google_not_synced:
            self.model.add_event(event, threaded=True)

        for g_id, event in local_synced.items():
            if g_id not in google_synced.keys():
                self.model.remove_event(event, threaded=True)
            elif not self.model.compare_events(event, google_synced[g_id]):
                self.model.update_event(event, updated_event=google_synced[g_id], threaded=True)

        self.event_loop.enqueue_threaded_event(CalendarSyncEvent(time.time()))

    def sync_deleted_events(self, service: Resource, email: str = None) -> None:
        for event in self.events_to_delete[email or AccountManager().current_account.email]:
            try:
                service.events().delete(calendarId="primary", eventId=event.google_id).execute()
            except HttpError as e:
                print(e)

        self.events_to_delete[email or AccountManager().current_account.email].clear()

    def sync_updated_events(self, service: Resource, email: str = None) -> None:
        for event in self.events_to_edit[email or AccountManager().current_account.email]:
            try:
                google_event = service.events().get(calendarId="primary", eventId=event.google_id).execute()

                google_event["summary"] = event.description
                if self.get_id_by_color(event.color) != 0:
                    google_event["colorId"] = str(self.get_id_by_color(event.color))

                google_event["start"] = {
                    "dateTime": event.date.strftime("%Y-%m-%d") + "T" + event.time.strftime("%H:%M") + ":00",
                    "timeZone": Config.time_zone
                }
                google_event["end"] = {
                    "dateTime": event.date.strftime("%Y-%m-%d") + "T" + event.time.strftime("%H:%M") + ":00",
                    "timeZone": Config.time_zone
                }

                if event.recurrence is EventRecurrence.MONTHLY:
                    google_event["recurrence"] = ["RRULE:FREQ=MONTHLY"]
                elif event.recurrence is EventRecurrence.YEARLY:
                    google_event["recurrence"] = ["RRULE:FREQ=YEARLY"]
                elif event.recurrence is EventRecurrence.WEEKLY:
                    day = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"][event.date.weekday()]
                    google_event["recurrence"] = ["RRULE:FREQ=WEEKLY;BYDAY=" + day]
                elif event.recurrence is EventRecurrence.NEVER and "recurrence" in google_event:
                    google_event.pop("recurrence")

                service.events().update(calendarId="primary", eventId=event.google_id, body=google_event).execute()

            except HttpError as e:
                print(e)

        self.events_to_edit[email or AccountManager().current_account.email].clear()

    def get_google_event_list(self, events: list[dict]) -> list[CalendarEvent]:
        ret = []
        for event in events:
            gid = event["id"]
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
                # time_zone = event["start"]["timeZone"]
                #
                # if time_zone.upper() != "UTC":
                #     tz = pytz.timezone(time_zone)
                #     date = tz.localize(date).astimezone(pytz.utc)

            recurrence = EventRecurrence.NEVER
            if "recurrence" in event:
                if event["recurrence"][0] == "RRULE:FREQ=MONTHLY":
                    recurrence = EventRecurrence.MONTHLY
                elif event["recurrence"][0] == "RRULE:FREQ=YEARLY":
                    recurrence = EventRecurrence.YEARLY
                elif "RRULE:FREQ=WEEKLY;BYDAY" in event["recurrence"][0]:
                    recurrence = EventRecurrence.WEEKLY

            calendar_event = CalendarEvent(0, date.date(), date.time(), description, color, recurrence, google_id=gid)
            ret.append(calendar_event)
        return ret

    def sync_calendars_threaded(self, email: str = None) -> None:
        def sync(on_complete):
            CalendarSyncManager().sync_calendars(email)
            on_complete()

        def callback():
            self.event_loop.enqueue_threaded_event(CalendarSyncEvent(time.time()))

        Thread(target=sync, args=(callback, )).start()

    def sync_all_calendars_threaded(self) -> None:
        def sync(on_complete):
            try:
                for user in AccountManager().accounts:
                    try:
                        CalendarSyncManager().sync_calendars_threaded(email=user.email)
                    except Exception as e:
                        print(e)
            finally:
                on_complete()

        def callback():
            self.event_loop.enqueue_threaded_event(CalendarSyncEvent(time.time()))

        Thread(target=sync, args=(callback, )).start()

    def add_event_to_google(self, service: Resource, event: CalendarEvent) -> str:
        summary = event.description
        dt = event.date.strftime("%Y-%m-%d") + "T" + event.time.strftime("%H:%M") + ":00"

        google_event = {
            "summary": summary,
            "start": {
                "dateTime": dt,
                "timeZone": Config.time_zone
            },
            "end": {
                "dateTime": dt,
                "timeZone": Config.time_zone
            }
        }

        if event.recurrence is EventRecurrence.WEEKLY:
            day = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"][datetime.datetime.fromisoformat(dt).weekday()]
            google_event["recurrence"] = ["RRULE:FREQ=WEEKLY;BYDAY=" + day]
        elif event.recurrence is EventRecurrence.MONTHLY:
            google_event["recurrence"] = ["RRULE:FREQ=MONTHLY"]
        elif event.recurrence is EventRecurrence.YEARLY:
            google_event["recurrence"] = ["RRULE:FREQ=YEARLY"]

        if self.get_id_by_color(event.color) != 0:
            google_event["colorId"] = str(self.get_id_by_color(event.color))

        google_event = service.events().insert(calendarId="primary", body=google_event).execute()
        return google_event.get("id")

    def update_event(self, event: CalendarEvent, updated_event: CalendarEvent = None, d: datetime.date = None,
                     t: datetime.time = None, description: str = None, color: Color = None,
                     recurrence: EventRecurrence = EventRecurrence.NEVER) -> None:

        if not event.google_id:
            return

        new_event = updated_event or CalendarEvent(event.id, d or event.date, t or event.time,
                                                   description or event.description, color or event.color,
                                                   recurrence or event.recurrence, google_id=event.google_id)

        self.events_to_edit[AccountManager().current_account.email].append(new_event)

    def remove_event(self, event: CalendarEvent) -> None:
        if not event.google_id:
            return

        self.events_to_delete[AccountManager().current_account.email].append(event)

    @staticmethod
    def get_color_by_id(color_id: str) -> Color:
        colors = [Colors.EVENT_BLUE204, Colors.EVENT_PINK204, Colors.EVENT_GREEN204, Colors.EVENT_PURPLE204,
                  Colors.EVENT_RED204, Colors.EVENT_YELLOW204, Colors.EVENT_ORANGE, None, None,
                  Colors.EVENT_BLUE, Colors.EVENT_GREEN, Colors.EVENT_RED]
        return colors[int(color_id)]

    @staticmethod
    def get_id_by_color(color: Color) -> int:
        colors = [Colors.EVENT_BLUE204, Colors.EVENT_PINK204, Colors.EVENT_GREEN204, Colors.EVENT_PURPLE204,
                  Colors.EVENT_RED204, Colors.EVENT_YELLOW204, Colors.EVENT_ORANGE, None, None,
                  Colors.EVENT_BLUE, Colors.EVENT_GREEN, Colors.EVENT_RED]
        return colors.index(color)
