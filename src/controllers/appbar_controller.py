import ctypes
import time
from typing import Callable
from ctypes import POINTER, WINFUNCTYPE, windll
from ctypes.wintypes import BOOL, HWND, RECT

import pyautogui
import pygame.display

from src.events.event import CloseWindowEvent, WindowResizeEvent, MouseClickEvent, MouseReleaseEvent, \
    MouseMotionEvent, WindowMinimizedEvent, WindowMoveEvent
from src.events.event_loop import EventLoop
from src.models.appbar_model import AppbarModel
from src.utils.pygame_utils import get_window_pos, get_window_size
from src.views.appbar_view import AppbarView


class AppbarController:

    def __init__(self, model: AppbarModel, view: AppbarView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.appbar_pressed = False
        self.pressed_pos = (0, 0)
        self.last_window_size = pygame.display.get_window_size()
        self.last_window_pos = get_window_pos()
        self.appbar_buttons_area_width = self.view.close_window_button.width * 3

        self.view.bind_on_click(self.on_appbar_click)
        self.view.bind_on_release(self.on_appbar_release)
        self.view.bind_on_mouse_motion(self.on_mouse_motion)

        self.view.bind_close_window(self.close_window)
        self.view.bind_resize_window(self.resize_window)
        self.view.bind_minimize_window(self.minimize_window)

    def on_appbar_click(self, event: MouseClickEvent) -> None:
        if self.view.x <= event.x < self.view.x + self.view.width and self.view.y <= event.y < self.view.y + self.view.height:
            self.appbar_pressed = True
            self.pressed_pos = pygame.mouse.get_pos()

            if self.is_maximized():
                rel_mouse_x = min(self.last_window_size[0] - self.appbar_buttons_area_width - 5, event.x * self.last_window_size[0] // get_window_size()[0])
                rel_mouse_y = event.y * self.last_window_size[1] // get_window_size()[1]
                self.pressed_pos = (rel_mouse_x, rel_mouse_y)
                new_size = self.last_window_size
                abs_mouse_pos = pyautogui.position()
                self.event_loop.enqueue_event(
                    WindowMoveEvent(time.time(), abs_mouse_pos[0] - rel_mouse_x, abs_mouse_pos[1] - rel_mouse_y)
                )
                self.view.change_resize_window_icon(True)
                self.event_loop.enqueue_event(WindowResizeEvent(time.time(), *new_size))

    def on_appbar_release(self, event: MouseReleaseEvent) -> None:
        self.appbar_pressed = False

    def on_mouse_motion(self, event: MouseMotionEvent) -> bool:
        if self.appbar_pressed:
            abs_mouse_pos = pyautogui.position()
            self.event_loop.enqueue_event(
                WindowMoveEvent(time.time(), abs_mouse_pos[0] - self.pressed_pos[0],
                                abs_mouse_pos[1] - self.pressed_pos[1])
            )
            return True

    def close_window(self) -> None:
        self.event_loop.enqueue_event(CloseWindowEvent(time.time()))

    def resize_window(self) -> None:
        screen_size = get_window_size()
        if not self.is_maximized():
            self.last_window_size = pygame.display.get_window_size()
            self.last_window_pos = get_window_pos()
            new_x = new_y = 0
            if (self.last_window_pos[0] + self.last_window_size[0] // 2) // get_window_size()[0] <= -1:
                new_x = -get_window_size()[0]
            elif (self.last_window_pos[1] + self.last_window_size[1] // 2) // get_window_size()[1] <= -1:
                new_y = -get_window_size()[1]
            new_size = screen_size
            self.event_loop.enqueue_event(WindowMoveEvent(time.time(), new_x, new_y))
        else:
            new_size = self.last_window_size
            self.event_loop.enqueue_event(
                WindowMoveEvent(time.time(), self.last_window_pos[0], self.last_window_pos[1])
            )
        self.view.change_resize_window_icon(pygame.display.get_window_size() == screen_size)
        self.event_loop.enqueue_event(WindowResizeEvent(time.time(), *new_size))

    def minimize_window(self) -> None:
        if not self.appbar_pressed:
            ctypes.windll.user32.ShowWindow(pygame.display.get_wm_info()["window"], 6)

    def is_maximized(self) -> bool:
        return pygame.display.get_window_size() == get_window_size()
