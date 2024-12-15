import time

from src.controllers.todo_list_controller import TodoListController
from src.events.event import OpenViewEvent, CloseViewEvent
from src.events.event_loop import EventLoop
from src.models.taskbar_model import TaskbarModel
from src.models.todo_list_model import TodoListModel
from src.views.calendar_view import CalendarView
from src.views.taskbar_view import TaskbarView
from src.views.todo_list_view import TodoListView
from src.views.view import View


class TaskbarController:

    def __init__(self, model: TaskbarModel, view: TaskbarView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.todo_list_opened = False
        self.todo_list_view = None

        self.view.bind_on_close(self.on_close)
        self.view.todo_list_button.bind_on_click(self.open_todo_list)
        self.view.calendar_view_button.bind_on_click(self.open_calendar_view)

    def open_todo_list(self) -> None:
        if self.todo_list_opened:
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.todo_list_view))
        else:
            model = TodoListModel()
            self.todo_list_view = TodoListView(
                self.view.display, model, self.event_loop, 300, self.view.display.get_height() - 30, 0, 0
            )
            TodoListController(model, self.todo_list_view, self.event_loop)
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), self.todo_list_view, False))

        self.todo_list_opened = not self.todo_list_opened

    def open_calendar_view(self) -> None:
        if self.todo_list_opened:
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.todo_list_view))
        else:
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), CalendarView, False))

    def on_close(self, view: View) -> None:
        if view == self.todo_list_view:
            self.todo_list_opened = False
