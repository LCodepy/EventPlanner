import time
from typing import Callable, Union

import pygame

from src.events.event import Event, MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, \
    MouseMotionEvent, AddTaskEvent, CloseViewEvent
from src.events.event_loop import EventLoop
from src.events.mouse_buttons import MouseButtons
from src.models.todo_list_model import TodoListModel, Task, TaskImportance
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.animations import ChangeValuesAnimation
from src.utils.assets import Assets
from src.views.view import View


class TodoTask(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), task: Task,
                 padding: Padding = None) -> None:
        super().__init__(canvas, pos, padding)

        self.canvas = canvas
        self.x, self.y = pos
        self.width, self.height = size
        self.task = task
        self.padding = padding
        self.id = task.id

        self.start_pos = (self.x, self.y)
        self.pressed = False
        self.click_pos = None

        self.on_delete_bind = None
        self.on_move = None
        self.on_release = None

        self.description_label = Label(
            self.canvas,
            (self.x - 10, self.y),
            (self.width - 50, self.height),
            text=self.task.description,
            text_color=(200, 200, 200),
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT,
            wrap_text=False
        )

        self.delete_task_button = Button(
            self.canvas,
            (self.x + self.width // 2 - Assets().delete_task_icon_large.get_width() // 2 - 5, self.y),
            (Assets().delete_task_icon_large.get_width(), Assets().delete_task_icon_large.get_height()),
            image=Assets().delete_task_icon_large,
            hover_image=Assets().delete_task_icon_large_hover,
            color=Colors.BACKGROUND_GREY22,
            hover_color=Colors.BACKGROUND_GREY22,
            click_color=Colors.BACKGROUND_GREY22,
            border_width=0
        )
        self.delete_task_button.bind_on_click(self.on_delete)

    def register_event(self, event: Event) -> bool:
        if self.delete_task_button.register_event(event):
            return True

        if (
            isinstance(event, MouseClickEvent) and
            self.get_rect().collidepoint((event.x, event.y)) and
            event.button is MouseButtons.LEFT_BUTTON
        ):
            self.pressed = True
            self.click_pos = (event.x, event.y)
            return True
        if isinstance(event, MouseReleaseEvent) and self.pressed and event.button is MouseButtons.LEFT_BUTTON:
            self.pressed = False
            self.on_release(self.id)
            return True
        if isinstance(event, MouseMotionEvent) and self.pressed:
            self.on_move(self.id, event.x, event.y)
            return True

    def render(self) -> None:
        if self.task.importance is TaskImportance.LOW:
            color = Colors.BLUE220
        elif self.task.importance is TaskImportance.MEDIUM:
            color = Colors.YELLOW220
        else:
            color = Colors.RED

        # Bez zaobljenih kutova
        # pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY22, self.get_rect())
        # pygame.draw.rect(self.canvas, color, [self.x - self.width // 2, self.y - self.height // 2, 4, self.height])

        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY22,
                         [self.get_rect().x + 8, self.get_rect().y, self.get_rect().w - 8, self.get_rect().h],
                         border_radius=5)
        pygame.draw.rect(self.canvas, color, [self.x - self.width // 2, self.y - self.height // 2, 4, self.height],
                         border_radius=2)

        self.description_label.render()
        self.delete_task_button.render()

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.description_label.canvas = self.canvas
        self.delete_task_button.canvas = self.canvas

    def update_position(self, x: int = None, y: int = None, set_start_pos: bool = False) -> None:
        if x is not None:
            self.description_label.x = x - 10
            self.delete_task_button.x = x + self.width // 2 - Assets().delete_task_icon_large.get_width() // 2 - 5
            self.x = x
            if set_start_pos:
                self.start_pos = (x, self.start_pos[1])
        if y is not None:
            self.description_label.y = y
            self.delete_task_button.y = y
            self.y = y
            if set_start_pos:
                self.start_pos = (self.start_pos[0], y)

    def on_delete(self) -> None:
        if self.on_delete_bind:
            self.on_delete_bind(self.id)

    def bind_on_delete(self, on_delete: Callable[[int], None]) -> None:
        self.on_delete_bind = on_delete

    def bind_on_move(self, on_move: Callable[[int, int, int], None]) -> None:
        self.on_move = on_move

    def bind_on_release(self, on_release: Callable[[int], None]) -> None:
        self.on_release = on_release

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)


class TodoListView(View):

    def __init__(self, display: pygame.Surface, model: TodoListModel, event_loop: EventLoop, width: int, height: int,
                 x: int = 0, y: int = 0) -> None:
        super().__init__(x, y)
        self.display = display
        self.model = model
        self.event_loop = event_loop
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.rendering = False

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.task_list_pos = (self.width // 2, 80)
        self.task_size = (self.width - 10, 40)
        self.tasks: dict[int, TodoTask] = {
            task.id: TodoTask(self.canvas, self.get_task_position(i), self.task_size, task)
            for i, task in enumerate(self.model.get_tasks())
        }

        self.move_task_animation = ChangeValuesAnimation("MoveTaskAnimation", self.event_loop, animation_time=0.2)
        self.current_animating_task_id = None

        self.move_task = None
        self.delete_task = None
        self.place_task = None

        self.deleted_events = []

        self.title_label = Label(
            self.canvas,
            (self.width // 2, 25),
            (100, 50),
            text="Todo List",
            text_color=(160, 160, 160),
            font=Assets().font24
        )

        self.add_task_button = Button(
            self.canvas,
            (self.width // 2, self.height - 40),
            (120, 40),
            label=Label(
                text="Add Task",
                text_color=(160, 160, 160),
                font=Assets().font18
            ),
            color=Colors.BLACK,
            hover_color=(50, 50, 50),
            click_color=(60, 60, 60),
            border_width=0,
            border_radius=3
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False
        self.deleted_events = []

        if isinstance(event, AddTaskEvent):
            new_id = self.model.get_next_id()
            task = Task(new_id, event.description, event.importance)
            self.model.add_task(task)
            self.tasks[new_id] = TodoTask(self.canvas, self.get_task_position(len(self.tasks)), self.task_size, task)
            self.bind_task_methods(task=self.tasks[new_id])
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), event.view))

        event = self.get_event(event)

        if self.title_label.register_event(event):
            registered_events = True
        if self.add_task_button.register_event(event):
            registered_events = True
        if self.move_task_animation.register_event(event):
            registered_events = True
            if self.move_task_animation.values:
                self.tasks[self.current_animating_task_id].update_position(*self.move_task_animation.values,
                                                                           set_start_pos=True)

        if not self.move_task_animation.active:
            for task in self.get_sorted_tasks():
                if task.register_event(event):
                    registered_events = True

        for task_id in self.deleted_events:
            self.tasks.pop(task_id)

        if self.deleted_events:
            self.update_task_list()

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        self.title_label.render()

        for task in self.get_sorted_tasks_for_rendering():
            task.render()

        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, (0, self.add_task_button.y - 40, self.width, 100))

        self.add_task_button.render()

        self.display.blit(self.canvas, (self.x, self.y))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.title_label.update_canvas(self.canvas)
        self.add_task_button.update_canvas(self.canvas)

        for task in self.get_sorted_tasks():
            task.update_canvas(self.canvas)

        self.add_task_button.update_position(y=self.height - 40)

    def update_task_list(self) -> None:
        for i, task in enumerate(self.get_sorted_tasks(key=lambda k: self.tasks[k].y)):
            task.update_position(y=self.get_task_position(i)[1], set_start_pos=True)

    def bind_task_methods(self, task: TodoTask = None) -> None:
        tasks = self.tasks.values()
        if task is not None:
            tasks = [task]
        for task in tasks:
            task.bind_on_delete(self.delete_task)
            task.bind_on_move(self.move_task)
            task.bind_on_release(self.place_task)

    def bind_delete_task(self, delete_task: Callable[[int], None]) -> None:
        self.delete_task = delete_task

    def bind_move_task(self, move_task: Callable[[int, int, int], None]) -> None:
        self.move_task = move_task

    def bind_place_task(self, place_task: Callable[[int], None]) -> None:
        self.place_task = place_task

    def bind_open_add_task_view(self, add_task: Callable[[], None]) -> None:
        self.add_task_button.bind_on_click(add_task)

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def get_task_position(self, idx: int) -> (int, int):
        return self.task_list_pos[0], self.task_list_pos[1] + idx * (self.task_size[1] + 5)

    def get_sorted_tasks(self, key: Callable = None) -> list[TodoTask]:
        return [self.tasks[k] for k in sorted(self.tasks.keys(), key=key or (lambda i: i))]

    def get_sorted_tasks_for_rendering(self) -> list[TodoTask]:
        if not self.tasks:
            return []
        for i in self.tasks:
            if self.tasks[i].pressed:
                break
        return [self.tasks[k] for k in self.tasks if k != i] + [self.tasks[i]]
