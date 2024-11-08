from abc import ABC, abstractmethod
from typing import Union

from src.events.event import Event, MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, \
    MouseMotionEvent


class View(ABC):

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.rendering = False

    @abstractmethod
    def register_event(self, event: Event) -> bool:
        """Registers event and returns true if rendering needed."""

    @abstractmethod
    def render(self) -> None:
        """Renders the view."""

    @abstractmethod
    def resize(self, width: int = None, height: int = None) -> None:
        """Resizes the view."""

    @abstractmethod
    def set_rendering(self, b: bool) -> None:
        """Sets rendering to ture or false."""

    @abstractmethod
    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent]) -> bool:
        """Returns true if event position is inside the view."""

    def get_event(self, event: Event) -> Event:
        if isinstance(event, (MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent)):
            return event.__class__(event.exec_time, event.x - self.x, event.y - self.y, *list(event.__dict__.values())[3:])
        elif isinstance(event, MouseMotionEvent):
            return MouseMotionEvent(
                event.exec_time, event.start_x - self.x, event.start_y - self.y, event.x - self.x, event.y - self.y
            )
        return event
