import datetime
import time

from src.controllers.event_list_controller import EventListController
from src.events.event import OpenViewEvent
from src.events.event_loop import EventLoop
from src.models.calendar_model import CalendarModel
from src.utils.calendar_functions import get_month_name
from src.views.calendar_view import CalendarView
from src.views.event_list_view import EventListView


class CalendarController:

    def __init__(self, model: CalendarModel, view: CalendarView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.view.previous_month_button.bind_on_click(self.change_to_previous_month)
        self.view.next_month_button.bind_on_click(self.change_to_next_month)
        self.view.bind_buttons = self.bind_calendar_buttons
        self.bind_calendar_buttons()
        self.view.bind_calendar_binding(self.bind_calendar_buttons)

    def change_to_previous_month(self) -> None:
        self.view.month -= 1
        if self.view.month < 1:
            self.view.month = 12
            self.view.year -= 1

        self.view.create_weekday_labels()
        self.view.create_day_buttons()

        self.view.month_label.set_text(get_month_name(self.view.month).upper())
        self.view.year_label.set_text(str(self.view.year))

        self.bind_calendar_buttons()

    def change_to_next_month(self) -> None:
        self.view.month += 1
        if self.view.month > 12:
            self.view.month = 1
            self.view.year += 1

        self.view.create_weekday_labels()
        self.view.create_day_buttons()

        self.view.month_label.set_text(get_month_name(self.view.month).upper())
        self.view.year_label.set_text(str(self.view.year))

        self.bind_calendar_buttons()

    def on_day_button_click(self, day: int) -> None:
        view = EventListView(self.view.display, self.model, self.event_loop, 300, self.view.display.get_height() - 30,
                             0, 0, datetime.date(self.view.year, self.view.month, day))
        EventListController(self.view.model, view, self.event_loop)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, False))

    def bind_calendar_buttons(self) -> None:
        for btn in self.view.day_buttons:
            day = int(btn.label.text)
            btn.bind_on_click(lambda d=day: self.on_day_button_click(d))

