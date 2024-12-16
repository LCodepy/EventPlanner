import time

from src.events.event import OpenEditTaskEvent, DeleteTaskEvent, CloseViewEvent, OpenEditCalendarEventEvent, \
    DeleteCalendarEventEvent
from src.events.event_loop import EventLoop
from src.models.calendar_model import CalendarEvent
from src.views.options_view import OptionsView


class OptionsController:

    def __init__(self, view: OptionsView, event_loop: EventLoop, task_id: int = None, event: CalendarEvent = None) -> None:
        self.view = view
        self.event_loop = event_loop
        self.task_id = task_id
        self.event = event

        self.view.edit_button.bind_on_click(self.edit)
        self.view.delete_button.bind_on_click(self.delete)

    def edit(self) -> None:
        if self.view.mode:
            self.event_loop.enqueue_event(OpenEditCalendarEventEvent(time.time(), self.event))
        else:
            self.event_loop.enqueue_event(OpenEditTaskEvent(time.time(), self.task_id))
        self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.view))

    def delete(self) -> None:
        if self.view.mode:
            self.event_loop.enqueue_event(DeleteCalendarEventEvent(time.time(), self.event))
        else:
            self.event_loop.enqueue_event(DeleteTaskEvent(time.time(), self.task_id))
        self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.view))

