from typing import Union, Callable

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, Event, MouseWheelUpEvent, MouseWheelDownEvent, \
    LanguageChangedEvent, MouseMotionEvent
from src.events.mouse_buttons import MouseButtons
from src.main.config import Config
from src.main.language_manager import LanguageManager
from src.ui.alignment import HorizontalAlignment
from src.ui.colors import Colors
from src.ui.label import Label
from src.utils.assets import Assets
from src.views.view import View


class SettingsView(View):

    def __init__(self, display: pygame.Surface, width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.on_click = None
        self.on_release = None
        self.on_mouse_motion = None
        self.on_scroll = None

        self.title_label = Label(
            self.canvas,
            (self.width // 2, 50),
            (self.width, 50),
            text="Settings",
            text_color=(200, 200, 200),
            font=Assets().font32
        )

        self.general_label = Label(
            self.canvas,
            (110, 142),
            (200, 40),
            text="General",
            text_color=(180, 180, 180),
            font=Assets().font24,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.language_label = Label(
            self.canvas,
            (120, 200),
            (200, 40),
            text="Choose a language:",
            text_color=(160, 160, 160),
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.show_catholic_events_label = Label(
            self.canvas,
            (170, 240),
            (300, 40),
            text="Show catholic events:",
            text_color=(160, 160, 160),
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, LanguageChangedEvent):
            self.update_language()

        event = self.get_event(event)

        for obj in self.get_ui_elements():
            if obj.register_event(event):
                registered_events = True

        if isinstance(event, MouseClickEvent) and self.on_click and event.button is MouseButtons.LEFT_BUTTON:
            self.on_click(event)
        elif isinstance(event, MouseReleaseEvent) and self.on_release and event.button is MouseButtons.LEFT_BUTTON:
            self.on_release(event)
        elif isinstance(event, MouseMotionEvent) and self.on_mouse_motion(event):
            return True

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        self.title_label.render()
        self.general_label.render()
        self.language_label.render()
        self.show_catholic_events_label.render()

        pygame.draw.line(self.canvas, Colors.GREY70, (10, 160), (self.width - 10, 160))

        pygame.draw.line(self.canvas, Colors.GREY70, (self.width - 1, 0), (self.width - 1, self.height))

        self.display.blit(self.canvas, (self.x, self.y))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height
        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

        self.title_label.x = self.width // 2

    def update_language(self) -> None:
        pass

    def bind_on_click(self, on_click: Callable[[MouseClickEvent], None]) -> None:
        self.on_click = on_click

    def bind_on_release(self, on_release: Callable[[MouseReleaseEvent], None]) -> None:
        self.on_release = on_release

    def bind_on_mouse_motion(self, on_mouse_motion: Callable[[MouseMotionEvent], bool]) -> None:
        self.on_mouse_motion = on_mouse_motion

    def bind_on_scroll(self, on_scroll: Callable[[Union[MouseWheelDownEvent, MouseWheelUpEvent]], bool]) -> None:
        self.on_scroll = on_scroll

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return Config.side_view_min_size

