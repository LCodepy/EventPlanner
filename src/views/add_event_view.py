import datetime
from typing import Union, Callable

import pygame

from src.events.event import Event, MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, \
    MouseWheelDownEvent, KeyReleaseEvent, LanguageChangedEvent
from src.events.event_loop import EventLoop
from src.models.calendar_model import CalendarEvent, EventRecurring
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.dropdown import DropDown
from src.ui.label import Label
from src.ui.text_field import TextField
from src.utils.assets import Assets
from src.main.language_manager import LanguageManager
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

        self.language_manager = LanguageManager()

        self.selected_color = None
        self.invalid_time_error = self.language_manager.get_string("invalid_time_error")
        self.editing_state = False
        self.event_to_edit = None

        self.colors = [
            Colors.EVENT_PINK204, Colors.EVENT_BLUE204, Colors.EVENT_GREEN204, Colors.EVENT_ORANGE, Colors.EVENT_RED204,
            Colors.EVENT_PURPLE204, Colors.EVENT_BLUE, Colors.EVENT_GREEN, Colors.EVENT_YELLOW204, Colors.EVENT_RED
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
            (self.width, 50),
            text=self.language_manager.get_string("add_event"),
            text_color=(160, 160, 160),
            font=Assets().font24
        )

        self.description_text_field = TextField(
            self.canvas,
            (self.width // 2, 170),
            (self.width - 80, 140),
            label=Label(text_color=(160, 160, 160), font=Assets().font18),
            hint=self.language_manager.get_string("event_description"),
            hint_text_color=(100, 100, 100),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            max_length=200
        )

        self.hours_input = TextField(
            self.canvas,
            (self.width // 4 - 25, 380),
            (40, 40),
            label=Label(text_color=(160, 160, 160), font=Assets().font24),
            hint="00",
            hint_text_color=(100, 100, 100),
            color=Colors.BACKGROUND_GREY30,
            border_width=0,
            max_length=2,
            allowed_char_set=set("0123456789"),
            underline=(160, 160, 160)
        )

        self.minutes_input = TextField(
            self.canvas,
            (self.width // 4 + 25, 380),
            (40, 40),
            label=Label(text_color=(160, 160, 160), font=Assets().font24),
            hint="00",
            hint_text_color=(100, 100, 100),
            color=Colors.BACKGROUND_GREY30,
            border_width=0,
            max_length=2,
            allowed_char_set=set("0123456789"),
            underline=(160, 160, 160)
        )

        self.recurring_label = Label(
            self.canvas,
            (self.width // 2 + 30, 380),
            (100, 40),
            text=self.language_manager.get_string("recurring"),
            text_color=(100, 100, 100),
            font=Assets().font20
        )

        self.dropdown = DropDown(
            self.canvas,
            (320, 380),
            (86, 34),
            self.language_manager.get_string("event_dropdown_options"),
            color=Colors.BACKGROUND_GREY22,
            border_color=(100, 100, 100),
            text_color=(160, 160, 160),
            font=Assets().font20,
            selected_option=3
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
            label=Label(text=self.language_manager.get_string("add"), text_color=(220, 220, 220), font=Assets().font18),
            border_width=0,
            border_radius=3
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, LanguageChangedEvent):
            self.update_language()

        event = self.get_event(event)

        for obj in self.get_ui_elements():
            if obj.register_event(event):
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

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        for obj in self.get_ui_elements():
            obj.render()

        for btn in self.color_buttons:
            btn.render()

        Label.render_text(self.canvas, ":", (self.width // 4, 378), Assets().font24, Colors.GREY140, True)

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

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

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

    def update_language(self) -> None:
        self.invalid_time_error = self.language_manager.get_string("invalid_time_error")
        self.add_event_label.set_text(self.language_manager.get_string("add_event"))
        self.description_text_field.set_hint(self.language_manager.get_string("event_description"))
        self.recurring_label.set_text(self.language_manager.get_string("recurring"))
        self.add_event_button.label.set_text(self.language_manager.get_string("add"))
        self.dropdown.update_options(self.language_manager.get_string("event_dropdown_options"))

    def get_time(self) -> datetime.time:
        return datetime.time(int(self.hours_input.text or "00"), int(self.minutes_input.text or "00"))

    def get_event_recurring(self) -> EventRecurring:
        options = self.language_manager.get_string("event_dropdown_options")

        if self.dropdown.get_selected_option() == options[3]:
            return EventRecurring.NEVER
        elif self.dropdown.get_selected_option() == options[0]:
            return EventRecurring.WEEKLY
        elif self.dropdown.get_selected_option() == options[1]:
            return EventRecurring.MONTHLY
        elif self.dropdown.get_selected_option() == options[2]:
            return EventRecurring.YEARLY

    def get_dropdown_option(self, option: EventRecurring) -> int:
        if option == EventRecurring.NEVER:
            return 3
        elif option == EventRecurring.WEEKLY:
            return 0
        elif option == EventRecurring.MONTHLY:
            return 1
        return 2

    def bind_on_add_button_click(self, on_click: Callable) -> None:
        self.add_event_button.bind_on_click(on_click)

    def bind_color_buttons(self, callback: Callable) -> None:
        for btn in self.color_buttons:
            btn.bind_on_click(callback(btn.color))

    def set_edit_state(self, event: CalendarEvent) -> None:
        self.editing_state = True
        self.event_to_edit = event

        self.add_event_label.set_text(self.language_manager.get_string("edit_event"))
        self.description_text_field.set_text(event.description)
        self.hours_input.set_text(str(event.time)[:2])
        self.minutes_input.set_text(str(event.time)[3:5])
        self.dropdown.set_option(self.get_dropdown_option(event.recurring))
        self.add_event_button.label.set_text(self.language_manager.get_string("apply"))

        for btn in self.color_buttons:
            if btn.color == event.color:
                btn.border_width = 2
                btn.border_color = Colors.WHITE
            else:
                btn.border_width = 0

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return self.width, self.height
