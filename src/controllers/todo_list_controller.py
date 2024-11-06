import time

import pygame.display

from src.controllers.add_task_controller import AddTaskController
from src.events.event import OpenViewEvent
from src.events.event_loop import EventLoop
from src.models.todo_list_model import TodoListModel
from src.views.add_task_view import AddTaskView
from src.views.todo_list_view import TodoListView


class TodoListController:

    def __init__(self, model: TodoListModel, view: TodoListView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.view.bind_delete_task(self.delete_task)
        self.view.bind_move_task(self.move_task)
        self.view.bind_place_task(self.place_task)
        self.view.bind_open_add_task_view(self.open_add_task_view)
        self.view.bind_task_methods()

    def delete_task(self, id_: int) -> None:
        self.view.deleted_events.append(id_)
        self.model.remove_task(id_)

    def move_task(self, id_: int, x: int, y: int) -> None:
        task = self.view.tasks[id_]
        x += task.start_pos[0] - task.click_pos[0]
        y += task.start_pos[1] - task.click_pos[1]
        new_x = min(max(x, self.view.task_list_pos[0] - 10), self.view.task_list_pos[0] + 10)
        new_y = min(max(y, self.view.task_list_pos[1] - 10), self.view.height)
        task.update_position(new_x, new_y)

    def place_task(self, id_: int) -> None:
        current_task = self.view.tasks[id_]

        closest = current_task.id
        min_distance = float("inf")
        for task in self.view.tasks.values():
            distance = (current_task.x - task.start_pos[0]) ** 2 + (current_task.y - task.start_pos[1]) ** 2
            if distance < min_distance:
                min_distance = distance
                closest = task.id

        if min_distance > current_task.height ** 2:
            closest = current_task.id
            self.view.current_animating_task_id = closest
            self.view.move_task_animation.start((self.view.tasks[current_task.id].x, self.view.tasks[current_task.id].y), [*current_task.start_pos])

        if closest == current_task.id:
            # current_task.update_position(*current_task.start_pos)
            return

        closest_pos = (self.view.tasks[closest].x, self.view.tasks[closest].y)
        self.view.current_animating_task_id = closest
        self.view.move_task_animation.start(list(closest_pos), [*current_task.start_pos])
        # self.view.tasks[closest].update_position(*current_task.start_pos, set_start_pos=True)
        current_task.update_position(*closest_pos, set_start_pos=True)

    def open_add_task_view(self) -> None:
        win_width, win_height = pygame.display.get_window_size()
        self.view.add_task_button.render_color = self.view.add_task_button.color
        view = AddTaskView(None, self.event_loop, 400, 500, win_width // 2 - 200, win_height // 2 - 250)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, True))
        AddTaskController(view, self.event_loop)
