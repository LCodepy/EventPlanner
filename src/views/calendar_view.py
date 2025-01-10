import datetime
from dataclasses import dataclass
from typing import Union, Callable

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, Event, MouseWheelUpEvent, MouseWheelDownEvent, \
    UpdateCalendarEvent, LanguageChangedEvent, CalendarSyncEvent, KeyPressEvent, ChangeMonthEvent
from src.main.config import Config
from src.models.calendar_model import CalendarModel, CalendarEvent
from src.ui.alignment import VerticalAlignment
from src.ui.button import Button
from src.ui.colors import Colors, Color
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.text_field import TextField
from src.utils.assets import Assets
from src.utils.calendar_functions import get_month_length, get_month_starting_day
from src.main.language_manager import LanguageManager
from src.views.view import View


@dataclass
class MonthEvent:

    event: CalendarEvent
    label: Label


class CalendarView(View):

    def __init__(self, display: pygame.Surface, model: CalendarModel,
                 width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.model = model
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.year = datetime.datetime.now().year
        self.month = datetime.datetime.now().month
        self.day = datetime.datetime.now().day
        self.weekday = datetime.datetime.now().weekday()

        self.today = datetime.datetime.today()

        self.year_input = TextField(
            self.canvas,
            (self.width // 2, 40),
            (80, 40),
            label=Label(text_color=(170, 170, 170), font=Assets().font32),
            border_width=0,
            underline=(170, 170, 170),
            color=(10, 10, 10),
            max_length=4,
            oneline=True,
            allowed_char_set=set("0123456789")
        )
        self.year_input.set_text(str(self.year))

        self.month_button = Button(
            self.canvas,
            (self.width // 2, 100),
            (200, 50),
            label=Label(text=self.get_month_name(self.month).upper(), text_color=(200, 200, 200), font=Assets().font36),
            border_width=0,
            border_radius=4,
            color=(10, 10, 10),
            hover_color=(30, 30, 30)
        )

        self.previous_month_button = Button(
            self.canvas,
            (self.width // 2 - 150, 100),
            (Assets().left_arrow_icon_large.get_width(), Assets().left_arrow_icon_large.get_height()),
            color=(10, 10, 10),
            hover_color=(10, 10, 10),
            click_color=(10, 10, 10),
            border_width=0,
            image=Assets().left_arrow_icon_large,
            hover_image=Assets().left_arrow_icon_large_hover
        )

        self.next_month_button = Button(
            self.canvas,
            (self.width // 2 + 150, 100),
            (Assets().right_arrow_icon_large.get_width(), Assets().right_arrow_icon_large.get_height()),
            color=(10, 10, 10),
            hover_color=(10, 10, 10),
            click_color=(10, 10, 10),
            border_width=0,
            image=Assets().right_arrow_icon_large,
            hover_image=Assets().right_arrow_icon_large_hover
        )

        self.weekday_labels = []
        self.create_weekday_labels()

        self.month_events: list[list[MonthEvent]] = [[] for _ in range(31)]

        self.day_buttons: list[Button] = []
        self.create_day_buttons()

        self.bind_buttons = None
        self.calendar_binding = None

    def create_weekday_labels(self) -> None:
        self.weekday_labels = [
            Label(
                self.canvas, (self.width * i // 8, 170), (50, 30),
                text=self.get_weekday_name(i), text_color=(170, 170, 170), font=Assets().font24
            ) for i in range(1, 8)
        ]

    def create_day_buttons(self) -> None:
        month_length = get_month_length(self.month)
        starting_day = get_month_starting_day(self.year, self.month)
        n_rows = ((month_length + starting_day) / 7).__ceil__()
        btn_height = (self.height - 300) // n_rows
        self.day_buttons = [
            Button(
                self.canvas, (self.width * (i % 7 + 1) // 8, 210 + i // 7 * (btn_height + 10) + btn_height // 2),
                (max(self.width // 8 - 10, 10), max(btn_height, 5)),
                label=Label(text=str(i - starting_day + 1), font=Assets().font18, text_color=(220, 220, 220),
                            vertical_text_alignment=VerticalAlignment.TOP),
                color=(10, 10, 10), border_color=self.get_day_button_color(i, starting_day), border_width=1,
                border_radius=10, padding=Padding(top=5)
            ) for i in range(starting_day, starting_day + month_length)
        ]

        self.month_events = [[] for _ in range(len(self.month_events))]
        for i, events in enumerate(self.model.get_events_for_month(self.year, self.month)):
            if not events:
                continue
            for j, event in enumerate(events):
                self.month_events[i].append(
                    MonthEvent(
                        event,
                        Label(
                            self.canvas, (self.day_buttons[i].x,
                                          self.day_buttons[i].y + 26 * j - self.day_buttons[i].height // 2 + 45),
                            (self.width // 8 - 30, 22), text=event.description, text_color=(200, 200, 200),
                            font=Assets().font14, wrap_text=False
                        )
                    )
                )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, LanguageChangedEvent):
            self.update_language()
        elif isinstance(event, KeyPressEvent) and event.keycode == pygame.K_RETURN and self.year_input.focused:
            self.set_year()
            registered_events = True
        elif isinstance(event, ChangeMonthEvent):
            self.month = event.month
            self.month_button.label.set_text(self.get_month_name(self.month).upper())
            self.create_day_buttons()
            self.calendar_binding()

        event = self.get_event(event)

        for obj in self.get_ui_elements():
            if obj.register_event(event):
                registered_events = True

        if isinstance(event, (UpdateCalendarEvent, CalendarSyncEvent, )):
            self.create_day_buttons()
            self.calendar_binding()
            registered_events = True

        for button in self.day_buttons:
            if button.register_event(event):
                registered_events = True

        return registered_events

    def render(self) -> None:
        self.canvas.fill((10, 10, 10))

        self.year_input.render()
        self.month_button.render()
        self.previous_month_button.render()
        self.next_month_button.render()
        for label in self.weekday_labels:
            label.render()
        for button in self.day_buttons:
            button.render()

        self.render_events()

        self.display.blit(self.canvas, (self.x, self.y))

    def render_events(self) -> None:
        for i in range(len(self.month_events)):
            next_y = 0
            last_rendered = -1
            for j, event in enumerate(self.month_events[i]):
                if self.day_buttons[i].height >= event.label.height * (j + 1) + 50:
                    last_rendered = j

            for j, event in enumerate(self.month_events[i]):
                if last_rendered == -1 and self.day_buttons[i].height < (j - 1) * 8 + 55:
                    continue

                collapsed = False
                width = event.label.width + 4
                if self.day_buttons[i].height < event.label.height * (j + 1) + 50 + (len(self.month_events[i]) - last_rendered - 1) * 4 or self.width < 500:
                    if j == 0:
                        next_y = event.label.y - event.label.height // 2
                    pygame.draw.rect(self.canvas, event.event.color, [event.label.x - width // 2, next_y - 1, width, 4],
                                     border_radius=100)
                    next_y += 8
                    collapsed = True
                else:
                    pygame.draw.rect(self.canvas, event.event.color, [event.label.x - width // 2,
                                                                      event.label.y - event.label.height // 2 - 1, width,
                                                                      event.label.height], border_radius=5, width=2)
                    next_y = event.label.y + event.label.height // 2 + 4

                    event.label.render()

                if self.day_buttons[i].hovering:
                    height = 4 if collapsed else event.label.height
                    surf2 = pygame.Surface((width, height), pygame.SRCALPHA)
                    surf2.fill((0, 0, 0, 0))
                    pygame.draw.rect(surf2, (0, 0, 0), [0, 0, width, height],
                                     border_radius=5, width=2)
                    surf2.set_alpha(30)
                    self.canvas.blit(
                        surf2, (event.label.x - width // 2, event.label.y - event.label.height // 2)
                    )

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height
        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

        self.create_weekday_labels()
        self.create_day_buttons()

        self.year_input.x = self.width // 2
        self.year_input.label.x = self.width // 2
        self.month_button.update_position(self.width // 2)
        self.previous_month_button.x = self.width // 2 - 150
        self.next_month_button.x = self.width // 2 + 150

        self.bind_buttons()

    def set_year(self) -> None:
        self.year_input.set_focus(False)
        year = self.year
        if self.year_input.text and int(self.year_input.text) > 0:
            self.year = int(self.year_input.text)
        else:
            self.year = datetime.datetime.now().year
            self.year_input.set_text(str(self.year))

        if self.year != year:
            self.create_day_buttons()
            self.calendar_binding()

    def update_language(self) -> None:
        self.create_day_buttons()
        self.create_weekday_labels()

    def get_day_button_color(self, idx: int, starting_day: int) -> Color:
        return Colors.RED if datetime.date(self.year, self.month, idx - starting_day + 1) == self.today.date() else (
            Colors.BLUE220 if (idx % 7) < 5 else (84, 168, 240))

    def bind_calendar_binding(self, calendar_binding: Callable) -> None:
        self.calendar_binding = calendar_binding

    def get_weekday_name(self, idx: int) -> str:
        return self.language_manager.get_string("days")[idx-1]

    def get_month_name(self, idx: int) -> str:
        return self.language_manager.get_string("months")[idx-1]

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return Config.main_view_min_size

