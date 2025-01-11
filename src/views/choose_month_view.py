from typing import Callable, Union

import pygame

from src.events.event import Event, MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, LanguageChangedEvent, \
    MouseWheelUpEvent, MouseWheelDownEvent
from src.events.event_loop import EventLoop
from src.main.language_manager import LanguageManager
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.label import Label
from src.utils.assets import Assets
from src.views.view import View


class ChooseMonthView(View):

    def __init__(self, display: pygame.Surface, event_loop: EventLoop, month: int,
                 width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.event_loop = event_loop
        self.month = month
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.rendering = False

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.shadow_canvas = pygame.Surface((self.width + 16, self.height + 16), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.on_create_buttons = None

        self.buttons: list[Button] = []
        self.create_buttons()

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, MouseMotionEvent) and self.is_focused(event):
            registered_events = True
            if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif isinstance(event, (MouseClickEvent, MouseReleaseEvent, )) and self.is_focused(event):
            registered_events = True
        elif isinstance(event, LanguageChangedEvent):
            self.update_language()

        event = self.get_event(event)

        for btn in self.buttons:
            if btn.register_event(event):
                registered_events = True

        return registered_events

    def render(self) -> None:
        self.canvas.fill((0, 0, 0, 0))

        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY22, [0, 0, self.width, self.height], border_radius=4)
        pygame.draw.rect(self.canvas, Colors.GREY70, [0, 0, self.width, self.height], width=1, border_radius=4)

        for btn in self.buttons:
            btn.render()

        self.shadow_canvas.fill((0, 0, 0, 0))
        for i in range(8):
            pygame.draw.rect(self.shadow_canvas, (0, 0, 0, max(110 - i * 11, 0)),
                             (8 - i, 0, self.width + 2*i, self.height + 2*i), border_radius=4 + 2*i, width=2)

        self.display.blit(self.shadow_canvas, (self.x-8, self.y))
        self.display.blit(self.canvas, (self.x, self.y))

    def create_buttons(self) -> None:
        self.buttons = [
            Button(
                self.canvas, (self.width // 2, 20 + i * 32), (self.width - 10, 30),
                label=Label(text=self.language_manager.get_string("months")[i].upper(),
                            text_color=Colors.TEXT_LIGHT_GREY, font=Assets().font24),
                color=Colors.BACKGROUND_GREY22,
                border_width=0,
                border_radius=4
            ) for i in range(12)
        ]

        if self.on_create_buttons:
            self.on_create_buttons()

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

    def bind_on_create_buttons(self, callback: Callable) -> None:
        self.on_create_buttons = callback

    def update_language(self) -> None:
        pass

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent,
                                      MouseMotionEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return self.width, self.height
