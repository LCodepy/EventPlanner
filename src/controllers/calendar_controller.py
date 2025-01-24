import datetime
import time

from src.controllers.choose_month_controller import ChooseMonthController
from src.controllers.event_list_controller import EventListController
from src.events.event import OpenViewEvent
from src.events.event_loop import EventLoop
from src.main.config import Config
from src.models.calendar_model import CalendarModel
from src.views.calendar_view import CalendarView
from src.views.choose_month_view import ChooseMonthView
from src.views.event_list_view import EventListView


class CalendarController:

    def __init__(self, model: CalendarModel, view: CalendarView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.view.year_input.bind_on_focus_changed(lambda f: self.view.set_year() if not f else None)
        self.view.month_button.bind_on_click(self.on_month_button_click)
        self.view.previous_month_button.bind_on_click(self.change_to_previous_month)
        self.view.next_month_button.bind_on_click(self.change_to_next_month)
        self.view.bind_buttons = self.bind_calendar_buttons
        self.bind_calendar_buttons()
        self.view.bind_calendar_binding(self.bind_calendar_buttons)

    def on_month_button_click(self) -> None:
        view = ChooseMonthView(
            self.view.display, self.event_loop, self.view.month, *Config.choose_month_view_size,
            self.view.x + self.view.width // 2 - Config.choose_month_view_size[0] // 2,
            self.view.y + self.view.month_button.y + Config.appbar_height
        )
        ChooseMonthController(view, self.event_loop)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, False))

    def change_to_previous_month(self) -> None:
        if self.view.month-1 < 1 and self.view.year < 2:
            return

        self.view.month -= 1
        if self.view.month < 1:
            self.view.month = 12
            self.view.year -= 1

        self.view.create_weekday_labels()
        self.view.create_day_buttons()

        self.view.month_button.label.set_text(self.view.get_month_name(self.view.month).upper())
        self.view.year_input.set_text(str(self.view.year))

        self.bind_calendar_buttons()

    def change_to_next_month(self) -> None:
        self.view.month += 1
        if self.view.month > 12:
            self.view.month = 1
            self.view.year += 1

        self.view.create_weekday_labels()
        self.view.create_day_buttons()

        self.view.month_button.label.set_text(self.view.get_month_name(self.view.month).upper())
        self.view.year_input.set_text(str(self.view.year))

        self.bind_calendar_buttons()

    def on_day_button_click(self, day: int) -> None:
        view = EventListView(
            self.view.display, self.model, self.event_loop, Config.side_view_width,
            self.view.display.get_height() - Config.appbar_height, 0, 0,
            datetime.date(self.view.year, self.view.month, day)
        )
        EventListController(self.view.model, view, self.event_loop)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, False))

    def bind_calendar_buttons(self) -> None:
        for btn in self.view.day_buttons:
            day = int(btn.label.text)
            btn.bind_on_click(lambda d=day: self.on_day_button_click(d))
