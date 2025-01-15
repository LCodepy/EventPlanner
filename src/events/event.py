import datetime
from dataclasses import dataclass, field
from typing import Any, Callable

from src.events.mouse_buttons import MouseButtons
from src.models.calendar_model import CalendarEvent, EventRecurrence
from src.models.todo_list_model import TaskImportance
from src.ui.colors import Color
from src.utils.authentication import User


@dataclass
class Event:

    exec_time: float


@dataclass
class ThreadedEvent(Event):

    def __init__(self, registered: bool = False):
        self.registered = registered


@dataclass
class MouseClickEvent(Event):

    x: int
    y: int
    button: MouseButtons


@dataclass
class MouseReleaseEvent(Event):

    x: int
    y: int
    button: MouseButtons


@dataclass
class MouseWheelUpEvent(Event):

    x: int
    y: int
    scroll: int


@dataclass
class MouseWheelDownEvent(Event):

    x: int
    y: int
    scroll: int


@dataclass
class MouseMotionEvent(Event):

    start_x: int
    start_y: int
    x: int
    y: int

    @property
    def move_vector(self) -> (int, int):
        return self.x - self.start_x, self.y - self.start_y


@dataclass
class KeyPressEvent(Event):

    keycode: int
    unicode: str


@dataclass
class KeyReleaseEvent(Event):

    keycode: int
    unicode: str


@dataclass
class RenderCursorEvent(Event):

    pass


@dataclass
class DeleteCharacterEvent(Event):

    pass


@dataclass
class MouseFocusChangedEvent(Event):

    focused: bool


@dataclass
class WindowResizeEvent(Event):

    width: int
    height: int


@dataclass
class WindowMoveEvent(Event):

    x: int
    y: int


@dataclass
class WindowMinimizedEvent(Event):

    pass


@dataclass
class WindowUnminimizedEvent(Event):

    pass


@dataclass
class CloseWindowEvent(Event):

    pass


@dataclass
class OpenViewEvent(Event):

    view: Any
    is_popup: bool


@dataclass
class CloseViewEvent(Event):

    view: Any


@dataclass
class ResizeViewEvent(Event):

    view: Any
    width: int = None
    height: int = None


@dataclass
class ShowIndependentLabelEvent(Event):

    label: Any


@dataclass
class HideIndependentLabelEvent(Event):

    pass


@dataclass
class AddTaskEvent(Event):

    description: str
    importance: TaskImportance


@dataclass
class DeleteTaskEvent(Event):

    id_: int


@dataclass
class EditTaskEvent(Event):

    id_: int
    description: str
    importance: TaskImportance


@dataclass
class OpenEditTaskEvent(Event):

    id_: int


@dataclass
class AddCalendarEventEvent(Event):

    time: datetime.time
    description: str
    color: Color
    recurrence: EventRecurrence


@dataclass
class DeleteCalendarEventEvent(Event):

    event: CalendarEvent


@dataclass
class EditCalendarEventEvent(Event):

    event: CalendarEvent
    time: datetime.time
    description: str
    color: Color
    recurrence: EventRecurrence


@dataclass
class DeleteCalendarEventEvent(Event):

    event: CalendarEvent


@dataclass
class OpenEditCalendarEventEvent(Event):

    event: CalendarEvent


@dataclass
class UpdateCalendarEvent(Event):

    pass


@dataclass
class ChangeMonthEvent(Event):

    month: int


@dataclass
class LanguageChangedEvent(Event):

    pass


@dataclass
class TimerEvent(Event):

    duration: float
    callback: Callable


@dataclass
class UserSignOutEvent(Event):

    user: User


@dataclass
class UserSignInEvent(ThreadedEvent):

    def __init__(self, exec_time: float, user: User, registered: bool = False):
        super().__init__(registered)
        self.exec_time = exec_time
        self.user = user
        self.registered = registered


@dataclass
class CalendarSyncEvent(ThreadedEvent):

    def __init__(self, exec_time: float, registered: bool = False):
        super().__init__(registered)
        self.exec_time = exec_time
        self.registered = registered


class EventFactory:

    @staticmethod
    def create_custom_event(event_name, dict_: dict = None) -> type:
        return type(event_name, (Event, ), dict_ or {})
