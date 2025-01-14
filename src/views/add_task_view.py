from typing import Union, Callable

import pygame

from src.events.event import Event, MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, \
    MouseWheelDownEvent, LanguageChangedEvent
from src.events.event_loop import EventLoop
from src.main.settings import Settings
from src.models.todo_list_model import TaskImportance
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.text_field import TextField
from src.utils.assets import Assets
from src.main.language_manager import LanguageManager
from src.utils.rendering import render_rounded_rect
from src.views.view import View


class AddTaskView(View):

    def __init__(self, display: pygame.Surface, event_loop: EventLoop, width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.event_loop = event_loop
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.rendering = False

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.on_importance_button_click = None
        self.editing_state = False
        self.task_to_edit = None

        self.close_button = Button(
            self.canvas,
            (self.width - 20, 20),
            (Assets().delete_task_icon_large.get_width(), Assets().delete_task_icon_large.get_height()),
            color=Colors.BACKGROUND_GREY30,
            border_width=0,
            apply_hover_effects=False,
            image=Assets().delete_task_icon_large,
            hover_image=Assets().delete_task_icon_large_hover
        )

        self.add_task_label = Label(
            self.canvas,
            (self.width // 2, 40),
            (150, 50),
            text=self.language_manager.get_string("add_task"),
            text_color=Colors.TEXT_GREY,
            font=Assets().font24
        )

        self.description_text_field = TextField(
            self.canvas,
            (self.width // 2, 190),
            (self.width - 60, 180),
            label=Label(text_color=Colors.TEXT_GREY, font=Assets().font18),
            hint=self.language_manager.get_string("task_description"),
            hint_text_color=Colors.TEXT_DARK_GREY,
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            max_length=200,
            border_radius=10
        )

        self.importance_label = Label(
            self.canvas,
            (self.width // 2, 320),
            (150, 30),
            text=self.language_manager.get_string("importance_level"),
            text_color=Colors.TEXT_GREY,
            font=Assets().font18
        )

        self.low_importance_button = Button(
            self.canvas,
            (self.width // 4 - 20, 370),
            (70, 40),
            color=Colors.BACKGROUND_GREY30,
            label=Label(text=self.language_manager.get_string("low"), text_color=(220, 220, 220), font=Assets().font18),
            border_color=Colors.GREY140,
            border_radius=10,
            padding=Padding(left=10)
        )
        self.low_importance_button.bind_on_click(self.on_low_importance_button_click)

        self.medium_importance_button = Button(
            self.canvas,
            (self.width // 2, 370),
            (70, 40),
            color=Colors.BACKGROUND_GREY30,
            label=Label(text=self.language_manager.get_string("mid"), text_color=(220, 220, 220), font=Assets().font18),
            border_color=Colors.GREY140,
            border_radius=10,
            padding=Padding(left=10)
        )
        self.medium_importance_button.bind_on_click(self.on_medium_importance_button_click)

        self.high_importance_button = Button(
            self.canvas,
            (self.width // 4 * 3 + 20, 370),
            (70, 40),
            color=Colors.BACKGROUND_GREY30,
            label=Label(text=self.language_manager.get_string("high"), text_color=(220, 220, 220), font=Assets().font18),
            border_color=Colors.GREY140,
            border_radius=10,
            padding=Padding(left=10)
        )
        self.high_importance_button.bind_on_click(self.on_high_importance_button_click)

        self.add_task_button = Button(
            self.canvas,
            (self.width // 2, 460),
            (100, 36),
            color=Colors.BLACK,
            hover_color=(50, 50, 50),
            click_color=(60, 60, 60),
            label=Label(text=self.language_manager.get_string("add"), text_color=(220, 220, 220), font=Assets().font18),
            border_width=0,
            border_radius=6
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, LanguageChangedEvent):
            self.update_language()

        event = self.get_event(event)

        for obj in self.get_ui_elements():
            if obj.register_event(event):
                registered_events = True

        return registered_events

    def render(self) -> None:
        self.canvas.fill((0, 0, 0, 0))

        if Settings().get_settings()["high_quality_graphics"]:
            render_rounded_rect(self.canvas, Colors.BACKGROUND_GREY30, pygame.Rect(0, 0, self.width, self.height), 20)
        else:
            pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, [0, 0, self.width, self.height], border_radius=20)

        for obj in self.get_ui_elements():
            obj.render()

        if Settings().get_settings()["high_quality_graphics"]:
            render_rounded_rect(self.canvas, Colors.BLUE220, pygame.Rect(self.width // 4 - 46, 364, 12, 12), 2)
            render_rounded_rect(self.canvas, Colors.YELLOW220, pygame.Rect(self.width // 2 - 26, 364, 12, 12), 2)
            render_rounded_rect(self.canvas, Colors.RED, pygame.Rect(self.width // 4 * 3 - 6, 364, 12, 12), 2)
        else:
            pygame.draw.rect(self.canvas, Colors.BLUE220, [self.width // 4 - 46, 364, 12, 12], border_radius=2)
            pygame.draw.rect(self.canvas, Colors.YELLOW220, [self.width // 2 - 26, 364, 12, 12], border_radius=2)
            pygame.draw.rect(self.canvas, Colors.RED, [self.width // 4 * 3 - 6, 364, 12, 12], border_radius=2)

        pygame.draw.line(self.canvas, Colors.GREY70, (20, 70), (self.width - 20, 70))

        self.display.blit(self.canvas, (self.x, self.y))

    def set_edit_state(self, id_: int, description: str, importance: TaskImportance) -> None:
        self.description_text_field.set_text(description)
        if importance is TaskImportance.LOW:
            self.on_low_importance_button_click()
        elif importance is TaskImportance.MEDIUM:
            self.on_medium_importance_button_click()
        elif importance is TaskImportance.HIGH:
            self.on_high_importance_button_click()
        self.add_task_button.label.set_text(self.language_manager.get_string("apply"))

        self.editing_state = True
        self.task_to_edit = id_

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

    def update_position(self, x: int = None, y: int = None) -> None:
        self.x = x or self.x
        self.y = y or self.y

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width
        self.height = height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.update_canvas(self.canvas)

    def update_language(self) -> None:
        self.add_task_label.set_text(self.language_manager.get_string("add_task"))
        self.description_text_field.set_hint(self.language_manager.get_string("task_description"))
        self.importance_label.set_text(self.language_manager.get_string("importance_level"))
        self.low_importance_button.label.set_text(self.language_manager.get_string("low"))
        self.medium_importance_button.label.set_text(self.language_manager.get_string("mid"))
        self.high_importance_button.label.set_text(self.language_manager.get_string("high"))
        self.add_task_button.label.set_text(self.language_manager.get_string("add"))

    def on_low_importance_button_click(self) -> None:
        self.low_importance_button.border_color = Colors.WHITE
        self.medium_importance_button.border_color = Colors.GREY140
        self.high_importance_button.border_color = Colors.GREY140
        if self.on_importance_button_click:
            self.on_importance_button_click(TaskImportance.LOW)

    def on_medium_importance_button_click(self) -> None:
        self.medium_importance_button.border_color = Colors.WHITE
        self.low_importance_button.border_color = Colors.GREY140
        self.high_importance_button.border_color = Colors.GREY140
        if self.on_importance_button_click:
            self.on_importance_button_click(TaskImportance.MEDIUM)

    def on_high_importance_button_click(self) -> None:
        self.high_importance_button.border_color = Colors.WHITE
        self.low_importance_button.border_color = Colors.GREY140
        self.medium_importance_button.border_color = Colors.GREY140
        if self.on_importance_button_click:
            self.on_importance_button_click(TaskImportance.HIGH)

    def bind_on_importance_button_click(self, on_click: Callable) -> None:
        self.on_importance_button_click = on_click

    def bind_on_add_button_click(self, on_click: Callable) -> None:
        self.add_task_button.bind_on_click(on_click)

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return self.width, self.height
