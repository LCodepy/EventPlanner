from abc import ABC
from typing import Callable, Union

import pygame

from src.events.event import Event, MouseClickEvent, MouseReleaseEvent, MouseMotionEvent, MouseWheelUpEvent, \
    MouseWheelDownEvent
from src.events.mouse_buttons import MouseButtons
from src.utils.pygame_utils import get_window_size
from src.utils.ui_debugger import UIDebugger
from src.views.view import View


class ResizingView(View):

    def __init__(self, display: pygame.Surface, width: int) -> None:
        super().__init__(0, 0)
        self.display = display
        self.width = width

        self.on_click = None
        self.on_release = None
        self.on_mouse_motion = None

    def register_event(self, event: Event) -> bool:
        if pygame.display.get_window_size() == get_window_size():
            return False
        if isinstance(event, MouseClickEvent) and event.button is MouseButtons.LEFT_BUTTON:
            if self.on_click(event):
                return True
        elif isinstance(event, MouseReleaseEvent) and event.button is MouseButtons.LEFT_BUTTON:
            if self.on_release(event):
                return True
        elif isinstance(event, MouseMotionEvent):
            if self.on_mouse_motion(event):
                return True

    def render(self) -> None:
        if UIDebugger.is_enabled():
            pygame.draw.rect(self.display, UIDebugger.box_color, self.get_rect(), 1)

    def resize(self, width: int = None, height: int = None) -> None:
        pass

    def set_rendering(self, b: bool) -> None:
        pass

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return False

    def bind_on_click(self, on_click: Callable[[MouseClickEvent], bool]) -> None:
        self.on_click = on_click

    def bind_on_release(self, on_release: Callable[[MouseReleaseEvent], bool]) -> None:
        self.on_release = on_release

    def bind_on_mouse_motion(self, on_mouse_motion: Callable[[MouseMotionEvent], bool]) -> None:
        self.on_mouse_motion = on_mouse_motion

    def get_rect(self) -> pygame.Rect:
        window_width, window_height = pygame.display.get_window_size()
        return pygame.Rect(self.width, self.width, window_width - self.width * 2, window_height - self.width * 2)
