import ctypes
import os
from typing import Callable, Union

import pyautogui as pyautogui
import pygame

from src.events.event import Event, MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, \
    MouseWheelDownEvent
from src.events.mouse_buttons import MouseButtons
from src.main.config import Config
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.image import Image
from src.ui.label import Label
from src.utils.assets import Assets
from src.views.view import View


class AppbarView(View):

    def __init__(self, display: pygame.Surface, width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.rendering = False

        self.on_click = None
        self.on_release = None
        self.on_mouse_motion = None

        self.close_window_button = Button(
            self.canvas,
            (self.canvas.get_width() - 25, 15),
            (50, 30),
            border_width=0,
            color=Colors.BACKGROUND_GREY22,
            hover_color=Colors.RED,
            click_color=(255, 80, 80),
            image=Assets().close_window_icon,
            hover_image=Assets().close_window_icon_hover
        )

        self.resize_window_button = Button(
            self.canvas,
            (self.canvas.get_width() - 75, 15),
            (50, 30),
            border_width=0,
            color=Colors.BACKGROUND_GREY22,
            hover_color=(50, 50, 50),
            click_color=(50, 50, 50),
            image=Assets().maximize_window_icon
        )

        self.minimize_window_button = Button(
            self.canvas,
            (self.canvas.get_width() - 125, 15),
            (50, 30),
            border_width=0,
            color=Colors.BACKGROUND_GREY22,
            hover_color=(50, 50, 50),
            click_color=(50, 50, 50),
            image=Assets().minimize_window_icon
        )

        self.app_icon = Image(
            self.canvas,
            (22, 14),
            Assets().app_icon
        )

        self.title_label = Label(
            self.canvas,
            (80, 15),
            (90, 30),
            text=Config.window_title,
            text_color=(180, 180, 180),
            font=Assets().font14
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False
        if self.minimize_window_button.register_event(event):
            registered_events = True
        if self.close_window_button.register_event(event):
            registered_events = True
        if self.resize_window_button.register_event(event):
            registered_events = True
        if self.app_icon.register_event(event):
            registered_events = True
        if self.title_label.register_event(event):
            registered_events = True

        if registered_events:
            return True

        if isinstance(event, MouseClickEvent) and self.on_click and event.button is MouseButtons.LEFT_BUTTON:
            self.on_click(event)
        elif isinstance(event, MouseReleaseEvent) and self.on_release and event.button is MouseButtons.LEFT_BUTTON:
            self.on_release(event)
        elif isinstance(event, MouseMotionEvent):
            if self.on_mouse_motion(event):
                return True

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY22)

        self.app_icon.render()
        self.title_label.render()

        self.close_window_button.render()
        self.resize_window_button.render()
        self.minimize_window_button.render()

        pygame.draw.line(self.canvas, (70, 70, 70), (0, self.height - 1), (self.width, self.height - 1))

        self.display.blit(self.canvas, (self.x, self.y))

    def change_resize_window_icon(self, maximize: bool) -> None:
        if maximize:
            self.resize_window_button.image = Assets().maximize_window_icon
        else:
            self.resize_window_button.image = Assets().shrink_window_icon

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height
        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.close_window_button.x = self.width - 25
        self.resize_window_button.x = self.width - 75
        self.minimize_window_button.x = self.width - 125

        self.close_window_button.canvas = self.canvas
        self.resize_window_button.canvas = self.canvas
        self.minimize_window_button.canvas = self.canvas
        self.app_icon.canvas = self.canvas
        self.title_label.canvas = self.canvas

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def bind_on_click(self, on_click: Callable[[MouseClickEvent], None]) -> None:
        self.on_click = on_click

    def bind_on_release(self, on_release: Callable[[MouseReleaseEvent], None]) -> None:
        self.on_release = on_release

    def bind_on_mouse_motion(self, on_mouse_motion: Callable[[MouseMotionEvent], bool]) -> None:
        self.on_mouse_motion = on_mouse_motion

    def bind_close_window(self, callback: Callable) -> None:
        self.close_window_button.bind_on_click(callback)

    def bind_resize_window(self, callback: Callable) -> None:
        self.resize_window_button.bind_on_click(callback)

    def bind_minimize_window(self, callback: Callable) -> None:
        self.minimize_window_button.bind_on_click(callback)

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return self.width, self.height

