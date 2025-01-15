import time
from typing import Union

import pygame

from src.events.event import MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, ResizeViewEvent, OpenViewEvent, \
    MouseWheelUpEvent, MouseWheelDownEvent
from src.events.event_loop import EventLoop
from src.main.config import Config
from src.views.settings_view import SettingsView


class SettingsController:

    def __init__(self, view: SettingsView, event_loop: EventLoop) -> None:
        self.view = view
        self.event_loop = event_loop

        self.pressed = False
        self.last_frame_interacted = False

        self.view.bind_on_click(self.on_click)
        self.view.bind_on_release(self.on_release)
        self.view.bind_on_mouse_motion(self.on_mouse_motion)
        self.view.bind_on_scroll(self.on_scroll)

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
        if event.x < 0 or event.x > self.view.width or event.y < 0 or event.y > self.view.height:
            return False

        scroll_value = Config.scroll_value * event.scroll
        min_y = self.view.general_label.get_rect().top
        max_y = self.view.sign_out_button.get_rect().bottom

        if (
            (isinstance(event, MouseWheelUpEvent) and min_y < 120) or
            (isinstance(event, MouseWheelDownEvent) and max_y > self.view.height - 30)
        ):
            if max_y + scroll_value <= self.view.height - 30:
                scroll_value = self.view.height - 30 - max_y
            elif min_y + scroll_value >= 120:
                scroll_value = 120 - min_y
            self.scroll(scroll_value)
            return True

    def scroll(self, scroll: int) -> None:
        for obj in self.view.get_ui_elements():
            if obj != self.view.title_label:
                obj.update_position(y=obj.y + scroll)
