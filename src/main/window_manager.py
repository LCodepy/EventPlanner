import time
from enum import Enum, auto

import pyautogui
import pygame

from src.events.event import Event, MouseClickEvent, MouseReleaseEvent, MouseMotionEvent, WindowResizeEvent, \
    WindowMoveEvent
from src.events.event_loop import EventLoop
from src.events.mouse_buttons import MouseButtons
from src.utils.pygame_utils import get_window_pos, get_window_size


class ResizeOrientation(Enum):

    N = auto()
    S = auto()
    E = auto()
    W = auto()
    NW = auto()
    NE = auto()
    SW = auto()
    SE = auto()


class WindowManager:

    def __init__(self, event_loop: EventLoop, width: int) -> None:
        self.event_loop = event_loop
        self.width = width

        self.pressed = False
        self.mouse_pressed = False
        self.resize_orientation = None

        self.last_window_y = None
        self.last_window_x = None

        self.interacted_last_frame = False

    def register_event(self, event: Event) -> bool:
        if pygame.display.get_window_size() == get_window_size():
            if isinstance(event, MouseClickEvent) and event.button is MouseButtons.LEFT_BUTTON:
                self.mouse_pressed = True
            elif isinstance(event, MouseReleaseEvent) and event.button is MouseButtons.LEFT_BUTTON:
                self.mouse_pressed = False
            return False
        if isinstance(event, MouseClickEvent) and event.button is MouseButtons.LEFT_BUTTON:
            if self.on_click(event):
                return True
        elif isinstance(event, MouseReleaseEvent) and event.button is MouseButtons.LEFT_BUTTON:
            if self.on_release(event):
                return True
        elif isinstance(event, MouseMotionEvent):
            if self.on_mouse_motion(event):
                return True

    def set_cursor(self) -> None:
        if self.pressed:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x >= self.get_rect().right and mouse_y >= self.get_rect().bottom:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
            self.resize_orientation = ResizeOrientation.SE
        elif mouse_x <= self.get_rect().left and mouse_y <= self.get_rect().top:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
            self.resize_orientation = ResizeOrientation.NW
        elif mouse_x >= self.get_rect().right and mouse_y <= self.get_rect().top:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENESW)
            self.resize_orientation = ResizeOrientation.NE
        elif mouse_x <= self.get_rect().left and mouse_y >= self.get_rect().bottom:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENESW)
            self.resize_orientation = ResizeOrientation.SW
        elif mouse_x >= self.get_rect().right:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            self.resize_orientation = ResizeOrientation.E
        elif mouse_x <= self.get_rect().left:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            self.resize_orientation = ResizeOrientation.W
        elif mouse_y >= self.get_rect().bottom:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)
            self.resize_orientation = ResizeOrientation.S
        elif mouse_y <= self.get_rect().top:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)
            self.resize_orientation = ResizeOrientation.N

    def on_click(self, event: MouseClickEvent) -> bool:
        self.mouse_pressed = True

        if not self.get_rect().collidepoint(event.x, event.y):
            self.pressed = True

            window_x, window_y = get_window_pos()
            window_width, window_height = pygame.display.get_window_size()

            if self.resize_orientation in (ResizeOrientation.N, ResizeOrientation.NE, ResizeOrientation.NW):
                self.last_window_y = window_y + window_height
            if self.resize_orientation in (ResizeOrientation.S, ResizeOrientation.SE, ResizeOrientation.SW):
                self.last_window_y = window_y
            if self.resize_orientation in (ResizeOrientation.E, ResizeOrientation.NE, ResizeOrientation.SE):
                self.last_window_x = window_x
            if self.resize_orientation in (ResizeOrientation.W, ResizeOrientation.NW, ResizeOrientation.SW):
                self.last_window_x = window_x + window_width

            return True

    def on_release(self, event: MouseReleaseEvent) -> bool:
        self.mouse_pressed = False
        if self.pressed:
            self.pressed = False
            return True
        self.pressed = False

    def on_mouse_motion(self, event: MouseMotionEvent) -> bool:
        if self.get_rect().collidepoint(event.x, event.y) and not self.pressed:
            if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW and self.interacted_last_frame:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            self.interacted_last_frame = False
        else:
            self.interacted_last_frame = True

            if self.pressed or not self.mouse_pressed:
                self.set_cursor()
            if not self.pressed:
                return False

            mouse_x, mouse_y = pyautogui.position()
            window_x, window_y = get_window_pos()
            window_width, window_height = pygame.display.get_window_size()

            if self.resize_orientation is ResizeOrientation.N:
                # if self.last_window_y - mouse_y <= 200:
                #     return True
                self.event_loop.enqueue_event(
                    WindowResizeEvent(time.time(), window_width, self.last_window_y - mouse_y)
                )
                self.event_loop.enqueue_event(WindowMoveEvent(time.time(), window_x, mouse_y))
            elif self.resize_orientation is ResizeOrientation.S:
                # if mouse_y - self.last_window_y <= 200:
                #     return True
                self.event_loop.enqueue_event(
                    WindowResizeEvent(time.time(), window_width, mouse_y - self.last_window_y)
                )
            elif self.resize_orientation is ResizeOrientation.E:
                # if mouse_x - self.last_window_x <= 270:
                #     return True
                self.event_loop.enqueue_event(
                    WindowResizeEvent(time.time(), mouse_x - self.last_window_x, window_height)
                )
            elif self.resize_orientation is ResizeOrientation.W:
                # if self.last_window_x - mouse_x <= 270:
                #     return True
                self.event_loop.enqueue_event(
                    WindowResizeEvent(time.time(), self.last_window_x - mouse_x, window_height)
                )
                self.event_loop.enqueue_event(WindowMoveEvent(time.time(), mouse_x, window_y))
            elif self.resize_orientation is ResizeOrientation.NE:
                # if self.last_window_y - mouse_y > 200:
                new_height = self.last_window_y - mouse_y
                # if mouse_x - self.last_window_x > 270:
                new_width = mouse_x - self.last_window_x
                self.event_loop.enqueue_event(
                    WindowResizeEvent(time.time(), new_width or window_width, new_height or window_height)
                )
                if new_height:
                    self.event_loop.enqueue_event(WindowMoveEvent(time.time(), window_x, mouse_y))
            elif self.resize_orientation is ResizeOrientation.NW:
                # if self.last_window_x - mouse_x > 270:
                new_width = self.last_window_x - mouse_x
                # if self.last_window_y - mouse_y > 200:
                new_height = self.last_window_y - mouse_y
                self.event_loop.enqueue_event(
                    WindowResizeEvent(time.time(), new_width or window_width, new_height or window_height)
                )
                self.event_loop.enqueue_event(
                    WindowMoveEvent(time.time(), mouse_x if new_width else window_x,
                                    mouse_y if new_height else window_y)
                )
            elif self.resize_orientation is ResizeOrientation.SW:
                # if self.last_window_x - mouse_x > 270:
                new_width = self.last_window_x - mouse_x
                # if mouse_y - self.last_window_y > 200:
                new_height = mouse_y - self.last_window_y
                self.event_loop.enqueue_event(
                    WindowResizeEvent(time.time(), new_width or window_width, new_height or window_height)
                )
                if new_width:
                    self.event_loop.enqueue_event(WindowMoveEvent(time.time(), mouse_x, window_y))
            elif self.resize_orientation is ResizeOrientation.SE:
                # if mouse_x - self.last_window_x > 270:
                new_width = mouse_x - self.last_window_x
                # if mouse_y - self.last_window_y > 200:
                new_height = mouse_y - self.last_window_y
                self.event_loop.enqueue_event(
                    WindowResizeEvent(time.time(), new_width or window_width, new_height or window_height)
                )

            return True

    def get_rect(self) -> pygame.Rect:
        win_width, win_height = pygame.display.get_window_size()
        return pygame.Rect(self.width, self.width, win_width - self.width * 2, win_height - self.width * 2)


