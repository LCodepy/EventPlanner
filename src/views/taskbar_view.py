from typing import Union

import pygame

from src.events.event import Event, MouseWheelUpEvent, MouseWheelDownEvent, MouseReleaseEvent, MouseClickEvent, \
    MouseMotionEvent
from src.models.taskbar_model import TaskbarModel
from src.ui.button import Button
from src.ui.colors import Colors
from src.utils.assets import Assets
from src.views.view import View


class TaskbarView(View):

    def __init__(self, display: pygame.Surface, model: TaskbarModel, width: int, height: int, x: int = 0, y: int = 0) -> None:
        super().__init__(x, y)
        self.display = display
        self.model = model
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.rendering = False

        self.profile_button = Button(
            self.canvas,
            (self.width // 2, self.width // 2),
            (self.width - 20, self.width - 20),
            color=Colors.BACKGROUND_GREY22,
            border_radius=(self.width - 20) // 2,
            border_width=0,
            apply_hover_effects=False,
            image=Assets().profile_picture_icon_large,
            hover_image=Assets().profile_picture_icon_large_hover
        )

        self.todo_list_button = Button(
            self.canvas,
            (self.width // 2 + 3, self.width // 2 + self.width),
            (self.width - 20, self.width - 20),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            apply_hover_effects=False,
            image=Assets().todo_list_icon_large,
            hover_image=Assets().todo_list_icon_large_hover
        )

        self.settings_button = Button(
            self.canvas,
            (self.width // 2, self.height - self.width // 2),
            (self.width - 20, self.width - 20),
            color=Colors.BACKGROUND_GREY22,
            border_radius=(self.width - 20) // 2,
            border_width=0,
            apply_hover_effects=False,
            image=Assets().settings_icon_large,
            hover_image=Assets().settings_icon_large_hover
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False
        event = self.get_event(event)

        if self.profile_button.register_event(event):
            registered_events = True
        if self.todo_list_button.register_event(event):
            registered_events = True
        if self.settings_button.register_event(event):
            registered_events = True

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY22)

        self.profile_button.render()
        self.todo_list_button.render()
        self.settings_button.render()

        pygame.draw.line(self.canvas, Colors.GREY70, (self.width - 1, 0), (self.width - 1, self.height))

        self.display.blit(self.canvas, (self.x, self.y))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height
        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.settings_button.y = self.height - self.width // 2

        self.profile_button.canvas = self.canvas
        self.todo_list_button.canvas = self.canvas
        self.settings_button.canvas = self.canvas

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height
