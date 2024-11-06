import time

from src.events.event import AddTaskEvent
from src.events.event_loop import EventLoop
from src.models.todo_list_model import TaskImportance
from src.views.add_task_view import AddTaskView


class AddTaskController:

    def __init__(self, view: AddTaskView, event_loop: EventLoop) -> None:
        self.view = view
        self.event_loop = event_loop

        self.importance = TaskImportance.LOW

        self.view.bind_on_importance_button_click(self.change_importance)
        self.view.bind_on_add_button_click(self.add_task)

    def change_importance(self, importance: TaskImportance) -> None:
        self.importance = importance

    def add_task(self) -> None:
        self.event_loop.enqueue_event(
            AddTaskEvent(time.time(), self.view.description_text_field.text, self.importance, self.view)
        )
