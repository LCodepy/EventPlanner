from typing import Union

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, Event
from src.models.calendar_model import CalendarModel
from src.views.view import View


class CalendarView(View):

    def __init__(self, display: pygame.Surface, model: CalendarModel,
                 width: int, height: int, x: int = 0, y: int = 0) -> None:
        super().__init__(x, y)

    def register_event(self, event: Event) -> bool:
        pass

    def render(self) -> None:
        pass

    def resize(self, width: int = None, height: int = None) -> None:
        pass

    def set_rendering(self, b: bool) -> None:
        pass

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent]) -> bool:
        pass
