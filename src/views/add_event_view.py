import datetime
import time
from typing import Union, Callable

import pygame

from src.events.event import Event, MouseClickEvent, MouseReleaseEvent, CloseViewEvent, MouseWheelUpEvent, \
    MouseWheelDownEvent, KeyReleaseEvent
from src.events.event_loop import EventLoop
from src.models.todo_list_model import TaskImportance
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.text_field import TextField
from src.utils.assets import Assets
from src.views.view import View


class AddEventView(View):

    def __init__(self, display: pygame.Surface, event_loop: EventLoop, width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.event_loop = event_loop
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.rendering = False

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.selected_color = None
        self.invalid_time_error = "Time is not valid."

        self.colors = [
            Colors.EVENT_GREEN204, Colors.EVENT_GREEN, Colors.EVENT_BLUE, Colors.EVENT_BLUE204, Colors.EVENT_PURPLE204,
            Colors.EVENT_PINK204, Colors.EVENT_RED, Colors.EVENT_RED204, Colors.EVENT_ORANGE, Colors.EVENT_YELLOW204
        ]
        self.color_buttons: list[Button] = []
        self.create_color_buttons()

        self.close_button = Button(
            self.canvas,
            (self.width - 20, 20),
            (Assets().delete_task_icon_large.get_width(), Assets().delete_task_icon_large.get_height()),
            color=Colors.BACKGROUND_GREY30,
            border_width=0,
            apply_hover_effects=False,
            image=Assets().delete_task_icon_large,
            hover_image=Assets().delete_task_icon_large_hover
        )

        self.add_event_label = Label(
            self.canvas,
            (self.width // 2, 40),
            (150, 50),
            text="Add Event",
            text_color=(160, 160, 160),
            font=Assets().font24
        )

        self.description_text_field = TextField(
            self.canvas,
            (self.width // 2, 170),
            (self.width - 80, 140),
            label=Label(text_color=(160, 160, 160), font=Assets().font18),
            hint="Event description...",
            hint_text_color=(100, 100, 100),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            max_length=200
        )

        self.hours_input = TextField(
            self.canvas,
            (self.width // 2 - 25, 380),
            (40, 40),
            label=Label(text_color=(160, 160, 160), font=Assets().font24),
            hint="00",
            hint_text_color=(100, 100, 100),
            color=Colors.BACKGROUND_GREY30,
            border_width=0,
            max_length=2,
            allowed_char_set=set("0123456789"),
            underline=(100, 100, 100)
        )

        self.minutes_input = TextField(
            self.canvas,
            (self.width // 2 + 25, 380),
            (40, 40),
            label=Label(text_color=(160, 160, 160), font=Assets().font24),
            hint="00",
            hint_text_color=(100, 100, 100),
            color=Colors.BACKGROUND_GREY30,
            border_width=0,
            max_length=2,
            allowed_char_set=set("0123456789"),
            underline=(100, 100, 100)
        )

        self.error_label = Label(
            self.canvas,
            (self.width // 2, 420),
            (self.width - 20, 40),
            text_color=Colors.RED,
            font=Assets().font18
        )

        self.add_event_button = Button(
            self.canvas,
            (self.width // 2, 460),
            (100, 36),
            color=Colors.BLACK,
            hover_color=(50, 50, 50),
            click_color=(60, 60, 60),
            label=Label(text="Add", text_color=(220, 220, 220), font=Assets().font18),
            border_width=0,
            border_radius=3
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        event = self.get_event(event)

        if self.close_button.register_event(event):
            registered_events = True
        if self.add_event_label.register_event(event):
            registered_events = True
        if self.description_text_field.register_event(event):
            registered_events = True
        if self.hours_input.register_event(event):
            registered_events = True
        if self.minutes_input.register_event(event):
            registered_events = True
        if self.add_event_button.register_event(event):
            registered_events = True

        for btn in self.color_buttons:
            if btn.register_event(event):
                registered_events = True

        if isinstance(event, KeyReleaseEvent) and event.keycode is pygame.K_TAB:
            if self.description_text_field.focused:
                self.description_text_field.set_focus(False)
                self.hours_input.set_focus(True)
            elif self.hours_input.focused:
                self.hours_input.set_focus(False)
                self.minutes_input.set_focus(True)
            elif self.minutes_input.focused:
                self.minutes_input.set_focus(False)
                self.description_text_field.set_focus(True)

        if registered_events:
            return True

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        self.close_button.render()
        self.add_event_label.render()
        self.description_text_field.render()
        self.hours_input.render()
        self.minutes_input.render()
        self.error_label.render()
        self.add_event_button.render()

        for btn in self.color_buttons:
            btn.render()

        Label.render_text(self.canvas, ":", (self.width // 2, 378), Assets().font24, Colors.GREY140, True)

        pygame.draw.line(self.canvas, Colors.GREY70, (20, 70), (self.width - 20, 70))

        self.display.blit(self.canvas, (self.x, self.y))

    def create_color_buttons(self) -> None:
        self.color_buttons = []

        n_cols = len(self.colors) // 2
        for i, color in enumerate(self.colors):
            self.color_buttons.append(
                Button(
                    self.canvas, (75 + (self.width - 150) // (n_cols + 1) * (i % n_cols + 1), 280 + (i >= n_cols) * 40),
                    (30, 30), color=color, border_width=0
                )
            )

    def show_error(self, error: str) -> None:
        self.error_label.set_text(error)

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.close_button.canvas = canvas
        self.add_event_label.canvas = self.canvas
        self.description_text_field.canvas = self.canvas
        self.hours_input.canvas = self.canvas
        self.minutes_input.canvas = self.canvas
        self.error_label.canvas = self.canvas
        self.add_event_button.canvas = self.canvas
        for btn in self.color_buttons:
            btn.update_canvas(self.canvas)

    def update_position(self, x: int = None, y: int = None) -> None:
        self.x = x or self.x
        self.y = y or self.y

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width
        self.height = height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.update_canvas(self.canvas)

    def get_time(self) -> datetime.time:
        return datetime.time(int(self.hours_input.text or "00"), int(self.minutes_input.text or "00"))

    def bind_on_add_button_click(self, on_click: Callable) -> None:
        self.add_event_button.bind_on_click(on_click)

    def bind_color_buttons(self, callback: Callable) -> None:
        for btn in self.color_buttons:
            btn.bind_on_click(callback(btn.color))

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def get_min_size(self) -> (int, int):
        return self.width, self.height
