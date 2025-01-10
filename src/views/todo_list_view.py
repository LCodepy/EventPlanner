import threading
from typing import Callable, Union

import pygame

from src.events.event import Event, MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, \
    MouseMotionEvent, AddTaskEvent, DeleteTaskEvent, CloseWindowEvent, EditTaskEvent, OpenEditTaskEvent, \
    LanguageChangedEvent
from src.events.event_loop import EventLoop
from src.events.mouse_buttons import MouseButtons
from src.main.config import Config
from src.models.todo_list_model import TodoListModel, Task, TaskImportance
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.animations import ChangeValuesAnimation
from src.utils.assets import Assets
from src.main.language_manager import LanguageManager
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
        self.pressed_right = False
        self.moving_task = False
        self.click_pos = None
        self.opened = False

        self.on_delete_bind = None
        self.on_move = None
        self.on_release = None
        self.on_open = None
        self.on_open_options = None
        self.open_edit_task_view = None

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

        if isinstance(event, DeleteTaskEvent) and event.id_ == self.id:
            self.on_delete()
        elif isinstance(event, OpenEditTaskEvent) and event.id_ == self.id:
            self.open_edit_task_view(self.id)

        if (
                isinstance(event, MouseClickEvent) and
                self.get_rect().collidepoint((event.x, event.y)) and
                event.button is MouseButtons.LEFT_BUTTON
        ):
            self.pressed = True
            self.click_pos = (event.x, event.y)
            return True
        elif (
                isinstance(event, MouseClickEvent) and
                self.get_rect().collidepoint((event.x, event.y)) and
                event.button is MouseButtons.RIGHT_BUTTON
        ):
            self.pressed_right = True
            self.click_pos = (event.x, event.y)
            return True
        elif isinstance(event, MouseReleaseEvent) and self.pressed and event.button is MouseButtons.LEFT_BUTTON:
            if not self.moving_task:
                self.opened = not self.opened
                self.on_open(self.id, self.opened)
            else:
                self.on_release(self.id)
            self.pressed = False
            self.moving_task = False
            return True
        elif isinstance(event, MouseReleaseEvent) and self.pressed_right and event.button is MouseButtons.RIGHT_BUTTON:
            self.on_open_options(self.id)
            self.pressed_right = False
            return True
        elif isinstance(event, MouseMotionEvent) and self.pressed:
            self.on_move(self.id, event.x, event.y)
            self.moving_task = True
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
        pygame.draw.rect(self.canvas, color, [self.get_rect().x, self.get_rect().y, 4, self.height],
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

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.description_label.resize(width=max(self.width - 50, 50), height=self.height)
        self.delete_task_button.x = self.x + self.width // 2 - Assets().delete_task_icon_large.get_width() // 2 - 5

    def resize_to_label_size(self, width: int) -> None:
        self.width = width

        if self.opened:
            self.description_label = Label(
                self.canvas,
                (self.x - 10, self.y),
                (max(self.width - 50, 50), self.height),
                text=self.task.description,
                text_color=(200, 200, 200),
                font=Assets().font18,
                horizontal_text_alignment=HorizontalAlignment.LEFT,
                wrap_text=True
            )
            self.description_label.height = self.description_label.get_min_label_size()[1] + 18
            self.height = self.description_label.get_min_label_size()[1] + 18
            return

        self.description_label.resize(width=max(self.width - 50, 50))

        self.delete_task_button.x = self.x + self.width // 2 - Assets().delete_task_icon_large.get_width() // 2 - 5

    def update(self) -> None:
        self.description_label.set_text(self.task.description)

    def on_delete(self) -> None:
        if self.on_delete_bind:
            self.on_delete_bind(self.id)

    def bind_on_delete(self, on_delete: Callable[[int], None]) -> None:
        self.on_delete_bind = on_delete

    def bind_on_move(self, on_move: Callable[[int, int, int], None]) -> None:
        self.on_move = on_move

    def bind_on_release(self, on_release: Callable[[int], None]) -> None:
        self.on_release = on_release

    def bind_on_open(self, on_open: Callable[[int, bool], None]) -> None:
        self.on_open = on_open

    def bind_on_open_options(self, on_open_options: Callable[[int], None]) -> None:
        self.on_open_options = on_open_options

    def bind_open_edit_task_view(self, open_edit_task_view: Callable[[int], None]) -> None:
        self.open_edit_task_view = open_edit_task_view

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - (self.height / 2).__ceil__(), self.width, self.height)


class TodoListView(View):

    def __init__(self, display: pygame.Surface, model: TodoListModel, event_loop: EventLoop, width: int, height: int,
                 x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.model = model
        self.event_loop = event_loop
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.rendering = False

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.task_list_pos = (self.width // 2, 90)
        self.task_size = (self.width - 10, 40)
        self.tasks: dict[int, TodoTask] = {
            task.id: TodoTask(self.canvas, (self.task_list_pos[0], self.get_task_position(task.idx)[1]), self.task_size, task)
            for task in self.model.get_tasks()
        }

        self.move_task_animations = {}

        self.move_task = None
        self.delete_task = None
        self.place_task = None
        self.open_task = None
        self.open_options = None
        self.open_edit_task_view = None

        self.on_click = None
        self.on_release = None
        self.on_mouse_motion = None
        self.on_scroll = None

        self.deleted_events = []

        self.title_label = Label(
            self.canvas,
            (self.width // 2, 35),
            (self.width, 50),
            text=self.language_manager.get_string("todo_list"),
            text_color=(160, 160, 160),
            font=Assets().font24
        )

        self.add_task_button = Button(
            self.canvas,
            (self.width // 2, self.height - 40),
            (120, 40),
            label=Label(
                text=self.language_manager.get_string("add_task"),
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

        if isinstance(event, CloseWindowEvent):
            self.save_tasks()

        if isinstance(event, AddTaskEvent):
            self.add_new_task(event)
        elif isinstance(event, EditTaskEvent):
            self.edit_task(event)
        elif isinstance(event, LanguageChangedEvent):
            self.update_language()

        event = self.get_event(event)

        if self.title_label.register_event(event):
            registered_events = True
        if self.add_task_button.register_event(event):
            registered_events = True

        for id_, anim in self.move_task_animations.items():
            if anim.register_event(event):
                registered_events = True
                if anim.values:
                    self.tasks[id_].update_position(*anim.values, set_start_pos=True)

        if not any(map(lambda a: a.active, self.move_task_animations.values())):
            for task in self.get_sorted_tasks():
                if task.register_event(event):
                    registered_events = True

        if isinstance(event, MouseClickEvent) and self.on_click and event.button is MouseButtons.LEFT_BUTTON:
            self.on_click(event)
        elif isinstance(event, MouseReleaseEvent) and self.on_release and event.button is MouseButtons.LEFT_BUTTON:
            self.on_release(event)
        elif isinstance(event, MouseMotionEvent) and self.on_mouse_motion(event):
            return True
        elif isinstance(event, (MouseWheelUpEvent, MouseWheelDownEvent)) and self.on_scroll(event):
            return True

        deleted_tasks = []
        for task_id in self.deleted_events:
            deleted_tasks.append(self.tasks.pop(task_id))

        if self.deleted_events:
            self.update_task_list(deleted_tasks)

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        for task in self.get_sorted_tasks_for_rendering():
            task.render()

        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, (0, 0, self.width, 50))
        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, (0, self.task_list_bottom[1], self.width, 100))

        self.render_shadow()

        self.title_label.render()
        self.add_task_button.render()

        pygame.draw.line(self.canvas, Colors.GREY70, (self.width - 1, 0), (self.width - 1, self.height))

        self.display.blit(self.canvas, (self.x, self.y))

    def render_shadow(self) -> None:
        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, [0, 0, self.width, 50])
        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, (0, self.task_list_bottom[1], self.width, 100))
        c = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
        for i in range(22):
            y = self.task_list_bottom[1] - i
            pygame.draw.line(c, (30, 30, 30, 255 - i * 12), (0, y), (self.width, y))
        self.canvas.blit(c, (0, 0))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.title_label.update_canvas(self.canvas)
        self.add_task_button.update_canvas(self.canvas)

        self.task_size = (self.width - 10, self.task_size[1])
        self.task_list_pos = (self.width // 2, self.task_list_pos[1])
        current_y = self.task_list_pos[1] - self.task_size[1] // 2
        for task in self.get_sorted_tasks():
            task.update_canvas(self.canvas)
            if width:
                task.resize_to_label_size(self.task_size[0])
                current_y += task.height
                task.update_position(x=self.width // 2, y=current_y - task.height // 2, set_start_pos=True)
                current_y += 5

        if width:
            self.title_label.x = self.width // 2
            self.add_task_button.update_position(x=self.width // 2)

        self.add_task_button.update_position(y=self.height - 40)

    def update_language(self) -> None:
        self.title_label.set_text(self.language_manager.get_string("todo_list"))
        self.add_task_button.label.set_text(self.language_manager.get_string("add_task"))

    def add_move_task_animation(self, id_: int, start: list[int], end: list[int]) -> None:
        self.move_task_animations[id_] = ChangeValuesAnimation(f"MoveTaskAnim{id_}", self.event_loop,
                                                               animation_time=0.2)
        self.move_task_animations[id_].start(start, end)

    def update_task_list(self, deleted_tasks: list[TodoTask]) -> None:
        deleted = deleted_tasks[0]

        for i, task in enumerate(self.get_sorted_tasks()):
            if task.y < deleted.y:
                continue
            task.update_position(y=task.y - deleted.height - 5, set_start_pos=True)
            self.update_task_idx(task.id, task.task.idx - 1)

    def add_new_task(self, event: AddTaskEvent) -> None:
        new_id = self.model.get_next_id()
        task = Task(new_id, event.description, event.importance, len(self.tasks))
        self.model.add_task(task)
        self.tasks[new_id] = TodoTask(self.canvas, self.get_new_task_position(), self.task_size, task)
        self.bind_task_methods(task=self.tasks[new_id])

    def edit_task(self, event: EditTaskEvent) -> None:
        self.tasks[event.id_].task = Task(event.id_, event.description, event.importance, self.tasks[event.id_].task.idx)
        self.tasks[event.id_].update()

    def update_task_idx(self, id_: int, idx: int) -> None:
        self.tasks[id_].task.idx = idx

    def save_tasks(self) -> None:
        def save_threaded(cls):
            for id_ in cls.tasks:
                task = cls.tasks[id_]
                cls.model.update_task(id_, description=task.task.description, importance=task.task.importance, idx=task.task.idx)

        thread = threading.Thread(target=save_threaded, args=(self, ))
        thread.start()

    def on_delete(self) -> None:
        self.save_tasks()

    def bind_task_methods(self, task: TodoTask = None) -> None:
        tasks = self.tasks.values()
        if task is not None:
            tasks = [task]
        for task in tasks:
            task.bind_on_delete(self.delete_task)
            task.bind_on_move(self.move_task)
            task.bind_on_release(self.place_task)
            task.bind_on_open(self.open_task)
            task.bind_on_open_options(self.open_options)
            task.bind_open_edit_task_view(self.open_edit_task_view)

    def bind_delete_task(self, delete_task: Callable[[int], None]) -> None:
        self.delete_task = delete_task

    def bind_move_task(self, move_task: Callable[[int, int, int], None]) -> None:
        self.move_task = move_task

    def bind_place_task(self, place_task: Callable[[int], None]) -> None:
        self.place_task = place_task

    def bind_open_task(self, open_task: Callable[[int, bool], None]) -> None:
        self.open_task = open_task

    def bind_open_options(self, open_options: Callable[[int], None]) -> None:
        self.open_options = open_options

    def bind_open_edit_task_view(self, open_edit_task_view: Callable[[int], None]) -> None:
        self.open_edit_task_view = open_edit_task_view

    def bind_open_add_task_view(self, add_task: Callable[[], None]) -> None:
        self.add_task_button.bind_on_click(add_task)

    def bind_on_click(self, on_click: Callable[[MouseClickEvent], None]) -> None:
        self.on_click = on_click

    def bind_on_release(self, on_release: Callable[[MouseReleaseEvent], None]) -> None:
        self.on_release = on_release

    def bind_on_mouse_motion(self, on_mouse_motion: Callable[[MouseMotionEvent], bool]) -> None:
        self.on_mouse_motion = on_mouse_motion

    def bind_on_scroll(self, on_scroll: Callable[[Union[MouseWheelDownEvent, MouseWheelUpEvent]], bool]) -> None:
        self.on_scroll = on_scroll

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def get_task_position(self, idx: int) -> (int, int):
        return self.task_list_pos[0], self.task_list_pos[1] + idx * (self.task_size[1] + 5)

    def get_new_task_position(self) -> (int, int):
        if self.tasks:
            last_task = self.get_sorted_tasks()[-1]
            return self.task_list_pos[0], last_task.y + last_task.height // 2 + self.task_size[1] // 2 + 5
        return self.task_list_pos

    def get_sorted_tasks(self, key: Callable = None) -> list[TodoTask]:
        return [self.tasks[k] for k in sorted(self.tasks.keys(), key=key or (lambda i: self.tasks[i].y))]

    def get_sorted_tasks_for_rendering(self) -> list[TodoTask]:
        if not self.tasks:
            return []
        for i in self.tasks:
            if self.tasks[i].pressed:
                break
        return [self.tasks[k] for k in self.tasks if k != i] + [self.tasks[i]]

    def get_min_size(self) -> (int, int):
        return Config.side_view_min_size

    @property
    def task_list_bottom(self) -> (int, int):
        return self.task_list_pos[0], self.add_task_button.y - 40

    @property
    def task_list_top(self) -> (int, int):
        return self.task_list_pos[0], self.task_list_pos[1] - self.task_size[1] // 2
