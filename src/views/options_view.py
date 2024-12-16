from typing import Union

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, Event, \
    MouseMotionEvent
from src.events.event_loop import EventLoop
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.image import Image
from src.ui.label import Label
from src.ui.padding import Padding
from src.utils.assets import Assets
from src.views.view import View


class OptionsView(View):

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

        self.mode = 0

        self.edit_button = Button(
            self.canvas,
            (self.width // 2, self.height // 4),
            (self.width - 6, self.height // 2 - 6),
            label=Label(text="Edit", text_color=(200, 200, 200), font=Assets().font18,
                        horizontal_text_alignment=HorizontalAlignment.LEFT),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            border_radius=2,
            padding=Padding(left=28)
        )

        self.delete_button = Button(
            self.canvas,
            (self.width // 2, self.height // 4 * 3),
            (self.width - 6, self.height // 2 - 6),
            label=Label(text="Delete", text_color=(200, 200, 200), font=Assets().font18,
                        horizontal_text_alignment=HorizontalAlignment.LEFT),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            border_radius=2,
            padding=Padding(left=28)
        )

        self.edit_icon = Image(
            self.canvas,
            (16, self.height // 4),
            Assets().edit_icon_large,
            Assets().edit_icon_large.get_size(),
        )

        self.delete_icon = Image(
            self.canvas,
            (16, self.height // 4 * 3),
            Assets().delete_task_icon_large,
            Assets().delete_task_icon_large.get_size(),
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, MouseMotionEvent) and self.is_focused(event):
            registered_events = True
            if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        event = self.get_event(event)

        if self.edit_button.register_event(event):
            registered_events = True
        if self.delete_button.register_event(event):
            registered_events = True

        return registered_events

    def render(self) -> None:
        self.canvas.fill((0, 0, 0, 0))

        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY22, [0, 0, self.width, self.height], border_radius=4)
        pygame.draw.rect(self.canvas, Colors.GREY70, [0, 0, self.width, self.height], width=1, border_radius=4)

        self.edit_button.render()
        self.delete_button.render()
        self.edit_icon.render()
        self.delete_icon.render()

        self.display.blit(self.canvas, (self.x, self.y))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width
        self.height = height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.edit_button.width = width - 4
        self.edit_button.height = height // 2 - 2
        self.edit_button.update_position(width // 2, height // 3)
        self.edit_button.update_canvas(self.canvas)
        self.delete_button.width = width - 4
        self.delete_button.height = height // 2 - 2
        self.delete_button.update_position(width // 2, height // 3 * 2)
        self.delete_button.update_canvas(self.canvas)
        self.edit_icon.canvas = self.canvas
        self.delete_icon.canvas = self.canvas

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def set_mode(self, m: int) -> None:
        self.mode = m

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, MouseMotionEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return self.width, self.height




