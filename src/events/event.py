import datetime
from dataclasses import dataclass
from typing import Any

from src.events.mouse_buttons import MouseButtons
from src.models.calendar_model import CalendarEvent
from src.models.todo_list_model import TaskImportance
from src.ui.colors import Color


@dataclass
class Event:

    exec_time: float


@dataclass
class MouseClickEvent(Event):

    exec_time: float
    x: int
    y: int
    button: MouseButtons


@dataclass
class MouseReleaseEvent(Event):

    exec_time: float
    x: int
    y: int
    button: MouseButtons


@dataclass
class MouseWheelUpEvent(Event):

    exec_time: float
    x: int
    y: int


@dataclass
class MouseWheelDownEvent(Event):

    exec_time: float
    x: int
    y: int


@dataclass
class MouseMotionEvent(Event):

    exec_time: float
    start_x: int
    start_y: int
    x: int
    y: int

    @property
    def move_vector(self) -> (int, int):
        return self.x - self.start_x, self.y - self.start_y


@dataclass
class KeyPressEvent(Event):

    exec_time: float
    keycode: int
    unicode: str


@dataclass
class KeyReleaseEvent(Event):

    exec_time: float
    keycode: int
    unicode: str


@dataclass
class RenderCursorEvent(Event):

    exec_time: float


@dataclass
class DeleteCharacterEvent(Event):

    exec_time: float


@dataclass
class MouseFocusChangedEvent(Event):

    exec_time: float
    focused: bool


@dataclass
class WindowResizeEvent(Event):

    exec_time: float
    width: int
    height: int


@dataclass
class WindowMoveEvent(Event):

    exec_time: float
    x: int
    y: int


@dataclass
class WindowMinimizedEvent(Event):

    exec_time: float


@dataclass
class WindowUnminimizedEvent(Event):

    exec_time: float


@dataclass
class CloseWindowEvent(Event):

    exec_time: float


@dataclass
class OpenViewEvent(Event):

    exec_time: float
    view: Any
    is_popup: bool


@dataclass
class CloseViewEvent(Event):

    exec_time: float
    view: Any


@dataclass
class ResizeViewEvent(Event):

    exec_time: float
    view: Any
    width: int = None
    height: int = None


@dataclass
class AddTaskEvent(Event):

    exec_time: float
    description: str
    importance: TaskImportance


@dataclass
class DeleteTaskEvent(Event):

    exec_time: float
    id_: int


@dataclass
class EditTaskEvent(Event):

    exec_time: float
    id_: int
    description: str
    importance: TaskImportance


@dataclass
class OpenEditTaskEvent(Event):

    exec_time: float
    id_: int


@dataclass
class AddCalendarEventEvent(Event):

    exec_time: float
    time: datetime.time
    description: str
    color: Color
    is_recurring: bool


@dataclass
class DeleteCalendarEventEvent(Event):

    exec_time: float
    event: CalendarEvent


@dataclass
class EditCalendarEventEvent(Event):

    exec_time: float
    event: CalendarEvent
    time: datetime.time
    description: str
    color: Color
    is_recurring: bool


@dataclass
class OpenEditCalendarEventEvent(Event):

    exec_time: float
    event: CalendarEvent


@dataclass
class UpdateCalendarEvent(Event):

    exec_time: float


class EventFactory:

    @staticmethod
    def create_custom_event(event_name, dict_: dict = None) -> type:
        return type(event_name, (Event, ), dict_ or {})
