import datetime
from typing import Union

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, Event, MouseWheelUpEvent, MouseWheelDownEvent
from src.models.calendar_model import CalendarModel
from src.ui.alignment import VerticalAlignment
from src.ui.button import Button
from src.ui.colors import Colors, darken
from src.ui.label import Label
from src.ui.padding import Padding
from src.utils.assets import Assets
from src.views.view import View


class CalendarView(View):

    def __init__(self, display: pygame.Surface, model: CalendarModel,
                 width: int, height: int, x: int = 0, y: int = 0) -> None:
        super().__init__(x, y)
        self.display = display
        self.model = model
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.year = datetime.datetime.now().year
        self.month = datetime.datetime.now().month
        self.day = datetime.datetime.now().day
        self.weekday = datetime.datetime.now().weekday()

        self.year_label = Label(
            self.canvas,
            (self.width // 2, 40),
            (80, 40),
            text=str(self.year),
            text_color=(170, 170, 170),
            font=Assets().font32
        )

        self.month_label = Label(
            self.canvas,
            (self.width // 2, 100),
            (200, 50),
            text=str(self.get_month_name(self.month).upper()),
            text_color=(200, 200, 200),
            font=Assets().font36
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

        self.day_buttons = []
        self.create_day_buttons()

    def create_weekday_labels(self) -> None:
        self.weekday_labels = [
            Label(
                self.canvas, (self.width * i // 8, 170), (50, 30),
                text=self.get_weekday_name(i), text_color=(170, 170, 170), font=Assets().font24
            ) for i in range(1, 8)
        ]

    def create_day_buttons(self) -> None:
        month_length = self.get_month_length(self.month)
        starting_day = self.get_month_starting_day(self.year, self.month)
        n_rows = ((month_length + starting_day) / 7).__ceil__()
        btn_height = (self.height - 300) // n_rows
        self.day_buttons = [
            Button(
                self.canvas, (self.width * (i % 7 + 1) // 8, 210 + i // 7 * (btn_height + 10) + btn_height // 2),
                (max(self.width // 8 - 10, 10), max(btn_height, 5)),
                label=Label(text=str(i - starting_day + 1), font=Assets().font18, text_color=(220, 220, 220),
                            vertical_text_alignment=VerticalAlignment.TOP),
                color=(10, 10, 10), border_color=Colors.BLUE220, border_width=1, border_radius=10, padding=Padding(top=5)
            ) for i in range(starting_day, starting_day + month_length)
        ]

    def register_event(self, event: Event) -> bool:
        registered_events = False

        event = self.get_event(event)

        if self.year_label.register_event(event):
            registered_events = True
        if self.month_label.register_event(event):
            registered_events = True
        if self.next_month_button.register_event(event):
            registered_events = True
        if self.previous_month_button.register_event(event):
            registered_events = True

        for button in self.day_buttons:
            if button.register_event(event):
                registered_events = True

        return registered_events

    def render(self) -> None:
        self.canvas.fill((10, 10, 10))

        self.year_label.render()
        self.month_label.render()
        self.previous_month_button.render()
        self.next_month_button.render()
        for label in self.weekday_labels:
            label.render()
        for button in self.day_buttons:
            button.render()

        self.display.blit(self.canvas, (self.x, self.y))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height
        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.year_label.canvas = self.canvas
        self.month_label.canvas = self.canvas
        self.previous_month_button.canvas = self.canvas
        self.next_month_button.canvas = self.canvas
        self.create_weekday_labels()
        self.create_day_buttons()

        self.year_label.x = self.width // 2
        self.month_label.x = self.width // 2
        self.previous_month_button.x = self.width // 2 - 150
        self.next_month_button.x = self.width // 2 + 150

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def get_min_size(self) -> (int, int):
        return 350, 450

    def get_month_name(self, month: int) -> str:
        return ["siječanj", "veljača", "ožujak", "travanj", "svibanj", "lipanj",
                "srpanj", "kolovoz", "rujan", "listopad", "studeni", "prosinac"][month-1]

    def get_weekday_name(self, weekday: int) -> str:
        return ["pon", "uto", "sri", "čet", "pet", "sub", "ned"][weekday-1]

    def get_month_length(self, month: int) -> int:
        if month == 2:
            return 28
        if month in (1, 3, 5, 7, 8, 10, 12):
            return 31
        return 30

    def get_month_starting_day(self, year: int, month: int) -> int:
        return datetime.datetime(year, month, 1).weekday()
