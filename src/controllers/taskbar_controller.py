from src.models.taskbar_model import TaskbarModel
from src.views.taskbar_view import TaskbarView


class TaskbarController:

    def __init__(self, model: TaskbarModel, view: TaskbarView) -> None:
        self.model = model
        self.view = view
