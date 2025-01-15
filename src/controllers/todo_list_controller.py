import time
from typing import Union

import pygame.display

from src.controllers.add_task_controller import AddTaskController
from src.controllers.options_controller import OptionsController
from src.events.event import OpenViewEvent, Event, MouseClickEvent, MouseReleaseEvent, MouseMotionEvent, \
    ResizeViewEvent, MouseWheelUpEvent, MouseWheelDownEvent
from src.events.event_loop import EventLoop
from src.main.config import Config
from src.models.todo_list_model import TodoListModel
from src.views.add_task_view import AddTaskView
from src.views.options_view import OptionsView
from src.views.todo_list_view import TodoListView, TodoTask


class TodoListController:

    def __init__(self, model: TodoListModel, view: TodoListView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.pressed = False
        self.last_frame_interacted = False

        self.view.bind_delete_task(self.delete_task)
        self.view.bind_move_task(self.move_task)
        self.view.bind_place_task(self.place_task)
        self.view.bind_open_task(self.open_task)
        self.view.bind_open_options(self.open_options)
        self.view.bind_open_edit_task_view(self.open_edit_task_view)
        self.view.bind_open_add_task_view(self.open_add_task_view)
        self.view.bind_on_click(self.on_click)
        self.view.bind_on_release(self.on_release)
        self.view.bind_on_mouse_motion(self.on_mouse_motion)
        self.view.bind_on_scroll(self.on_scroll)
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

        closest_task = current_task
        min_distance = float("inf")
        for task in self.view.tasks.values():
            distance = (current_task.x - task.start_pos[0]) ** 2 + (current_task.y - task.start_pos[1]) ** 2
            if distance < min_distance:
                min_distance = distance
                closest_task = task

        if min_distance > current_task.height ** 2 or closest_task.id == current_task.id:
            closest_task = current_task
            self.view.add_move_task_animation(
                closest_task.id, [self.view.tasks[current_task.id].x, self.view.tasks[current_task.id].y],
                [*current_task.start_pos]
            )
        if closest_task.id == current_task.id:
            return

        # self.switch_tasks(current_task, closest_task)
        self.move_tasks(current_task, closest_task)

    def switch_tasks(self, current_task: TodoTask, closest_task: TodoTask) -> None:
        # TODO: ne radi, mora ispravno updejtat taskove
        closest_pos = (closest_task.x, closest_task.y - current_task.height // 2 + closest_task.height // 2)
        replaced_task_y = current_task.start_pos[1] - current_task.height // 2 + closest_task.height // 2
        added_height = closest_task.height - current_task.height

        if closest_task.start_pos[1] <= current_task.start_pos[1]:
            closest_pos = (closest_task.x, closest_task.y - closest_task.height // 2 + current_task.height // 2)
            replaced_task_y = current_task.start_pos[1] + current_task.height // 2 - closest_task.height // 2
            added_height = -added_height

        self.view.add_move_task_animation(
            closest_task.id, [closest_task.x, closest_task.y],
            [current_task.start_pos[0], replaced_task_y]
        )
        # self.model.update_task(closest_task.id, idx=current_task.task.idx)
        self.view.update_task_idx(closest_task.id, current_task.task.idx)

        for task in self.view.get_sorted_tasks():
            if (
                    min(current_task.start_pos[1], closest_task.start_pos[1]) < task.y <
                    max(current_task.start_pos[1], closest_task.start_pos[1]) and
                    task.id not in (current_task.id, closest_task.id)
            ):
                self.view.add_move_task_animation(
                    task.id, list(task.start_pos), [task.start_pos[0], task.start_pos[1] + added_height]
                )

        current_task.update_position(*closest_pos, set_start_pos=True)
        # self.model.update_task(current_task.id, idx=closest_task.task.idx)
        self.view.update_task_idx(current_task.id, closest_task.task.idx)

    def move_tasks(self, current_task: TodoTask, closest_task: TodoTask) -> None:
        closest_pos = (closest_task.x, closest_task.y - current_task.height // 2 + closest_task.height // 2)
        added_height = -current_task.height - 5

        if closest_task.start_pos[1] <= current_task.start_pos[1]:
            closest_pos = (closest_task.x, closest_task.y - closest_task.height // 2 + current_task.height // 2)
            added_height = -added_height

        self.view.update_task_idx(current_task.id, closest_task.task.idx)

        for task in self.view.get_sorted_tasks():
            if (
                min(current_task.start_pos[1], closest_task.start_pos[1]) <= task.y <=
                max(current_task.start_pos[1], closest_task.start_pos[1]) and task.id != current_task.id
            ):
                self.view.add_move_task_animation(
                    task.id, list(task.start_pos), [task.start_pos[0], task.start_pos[1] + added_height]
                )
                if added_height < 0:
                    self.view.update_task_idx(task.id, task.task.idx - 1)
                else:
                    self.view.update_task_idx(task.id, task.task.idx + 1)

        current_task.update_position(*closest_pos, set_start_pos=True)

    def open_task(self, id_: int, opened: bool) -> None:
        task = self.view.tasks[id_]
        task_y = task.y
        task_height = task.height

        task.description_label.set_wrap_text(opened)
        if opened:
            if len(task.description_label.lines) <= 1:
                task.description_label.set_wrap_text(not opened)
                return
            task.description_label.resize(height=task.description_label.get_min_label_size()[1] + 18)
            task.resize(height=task.description_label.height)
            task.update_position(y=task.y + task.height // 2 - self.view.task_size[1] // 2, set_start_pos=True)
            task.delete_task_button.update_position(y=task.y - task.height // 2 + task.delete_task_button.height)
        else:
            task.update_position(y=task.y - task.height // 2 + self.view.task_size[1] // 2, set_start_pos=True)
            task.description_label.resize(height=self.view.task_size[1])
            task.resize(height=self.view.task_size[1])

        for todo_task in self.view.get_sorted_tasks():
            if todo_task.id == id_ or todo_task.y < (task_y if opened else task.y):
                continue
            new_y = todo_task.y + task.height - self.view.task_size[1] if opened else todo_task.y - task_height + self.view.task_size[1]
            todo_task.update_position(y=new_y, set_start_pos=True)

    def open_options(self, id_: int) -> None:
        x, y = pygame.mouse.get_pos()
        if y > self.view.height - Config.options_view_size[1] * 2:
            y -= Config.options_view_size[1]
        options = OptionsView(self.view.display, self.event_loop, *Config.options_view_size, x, y)
        OptionsController(options, self.event_loop, task_id=id_)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), options, False))

    def open_edit_task_view(self, id_: int) -> None:
        win_width, win_height = pygame.display.get_window_size()
        view = AddTaskView(
            self.view.display, self.event_loop, *Config.top_view_size,
            win_width // 2 - Config.top_view_size[0] // 2,
            win_height // 2 - Config.top_view_size[1] // 2 + Config.appbar_height // 2
        )
        task = self.view.tasks[id_].task
        AddTaskController(view, self.event_loop)
        view.set_edit_state(id_, task.description, task.importance)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, True))

    def open_add_task_view(self) -> None:
        win_width, win_height = pygame.display.get_window_size()
        view = AddTaskView(
            self.view.display, self.event_loop, *Config.top_view_size,
            win_width // 2 - Config.top_view_size[0] // 2,
            win_height // 2 - Config.top_view_size[1] // 2 + Config.appbar_height // 2
        )
        AddTaskController(view, self.event_loop)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, True))

    def on_click(self, event: MouseClickEvent) -> None:
        if self.view.width - 5 < event.x < self.view.width and 0 < event.y < self.view.height:
            self.pressed = True

    def on_release(self, event: MouseReleaseEvent) -> None:
        self.pressed = False

    def on_mouse_motion(self, event: MouseMotionEvent) -> bool:
        if event.y < 0:
            if self.last_frame_interacted:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.last_frame_interacted = False
            return False
        if (
            pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_SIZEWE and
            (self.view.width - 5 < event.x < self.view.width or self.pressed)
        ):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            self.last_frame_interacted = True
        elif pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW and self.last_frame_interacted:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.last_frame_interacted = False

        if self.pressed:
            self.event_loop.enqueue_event(
                ResizeViewEvent(
                    time.time(), self.view, min(max(event.x, self.view.get_min_size()[0]), Config.side_view_max_width)
                )
            )
            return True

    def on_scroll(self, event: Union[MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        if event.x < 0 or event.x > self.view.width or event.y < 0 or event.y > self.view.height or not self.view.tasks:
            return False

        scroll_value = Config.scroll_value * event.scroll
        min_y = self.view.get_sorted_tasks()[0].get_rect().top
        max_y = self.view.get_sorted_tasks()[-1].get_rect().bottom

        if (
            (isinstance(event, MouseWheelUpEvent) and
             min_y < self.view.task_list_top[1]) or
            (isinstance(event, MouseWheelDownEvent) and
             max_y > self.view.task_list_bottom[1])
        ):
            if max_y + scroll_value <= self.view.task_list_bottom[1]:
                scroll_value = self.view.task_list_bottom[1] - max_y
            elif min_y + scroll_value >= self.view.task_list_top[1]:
                scroll_value = self.view.task_list_top[1] - min_y
            self.scroll_tasks(scroll_value)
            return True

    def scroll_tasks(self, scroll: int = 0) -> None:
        for task in self.view.get_sorted_tasks():
            task.update_position(y=task.y + scroll, set_start_pos=True)

