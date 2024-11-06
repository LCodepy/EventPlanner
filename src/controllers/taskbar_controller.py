import time

from src.controllers.todo_list_controller import TodoListController
from src.events.event import OpenViewEvent, CloseViewEvent
from src.events.event_loop import EventLoop
from src.models.taskbar_model import TaskbarModel
from src.models.todo_list_model import TodoListModel
from src.views.taskbar_view import TaskbarView
from src.views.todo_list_view import TodoListView


class TaskbarController:

    def __init__(self, model: TaskbarModel, view: TaskbarView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.todo_list_opened = False
        self.todo_list_view = None

        self.view.todo_list_button.bind_on_click(self.open_todo_list)

    def open_todo_list(self) -> None:
        if self.todo_list_opened:
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.todo_list_view))
        else:
            model = TodoListModel()
            self.todo_list_view = TodoListView(None, model, self.event_loop, 300, self.view.display.get_height() - 30,
                                               x=self.view.width, y=30)
            TodoListController(model, self.todo_list_view, self.event_loop)
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), self.todo_list_view, False))

        self.todo_list_opened = not self.todo_list_opened
