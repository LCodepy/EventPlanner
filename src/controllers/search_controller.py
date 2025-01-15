import time
from typing import Union

import pygame

from src.controllers.event_list_controller import EventListController
from src.events.event import MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, ResizeViewEvent, OpenViewEvent, \
    MouseWheelUpEvent, MouseWheelDownEvent
from src.events.event_loop import EventLoop
from src.main.config import Config
from src.models.calendar_model import CalendarModel, CalendarEvent
from src.views.event_list_view import EventListView
from src.views.search_view import SearchView


class SearchController:

    def __init__(self, model: CalendarModel, view: SearchView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.pressed = False
        self.last_frame_interacted = False

        self.view.bind_on_click(self.on_click)
        self.view.bind_on_release(self.on_release)
        self.view.bind_on_mouse_motion(self.on_mouse_motion)
        self.view.bind_on_scroll(self.on_scroll)

        self.view.search_bar.bind_on_key(self.on_search_bar_typed)
        self.view.bind_on_search_event_release(self.on_search_event_release)

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
            self.view.search_bar.set_focus(False)
            return True

    def on_scroll(self, event: Union[MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        if event.x < 0 or event.x > self.view.width or event.y < 0 or event.y > self.view.height or not self.view.events:
            return False

        scroll_value = Config.scroll_value * event.scroll
        min_y = self.view.events[0].get_rect().centery
        max_y = self.view.events[-1].get_rect().bottom

        if (
            (isinstance(event, MouseWheelUpEvent) and
             min_y < self.view.event_list_start_pos[1]) or
            (isinstance(event, MouseWheelDownEvent) and
             max_y > self.view.height - 30)
        ):
            if max_y + scroll_value <= self.view.height - 30:
                scroll_value = self.view.height - 30 - max_y
            elif min_y + scroll_value >= self.view.event_list_start_pos[1]:
                scroll_value = self.view.event_list_start_pos[1] - min_y
            self.scroll_events(scroll_value)
            return True

    def scroll_events(self, scroll: int = 0) -> None:
        for event in self.view.events:
            event.update_position(y=event.y + scroll)

    def on_search_bar_typed(self) -> None:
        query = self.view.search_bar.text

        search_results = []
        if query:
            search_results = self.model.search_events(query)

        self.view.create_search_events(search_results)
        self.view.bind_search_event_methods()

    def on_search_event_release(self, event: CalendarEvent) -> None:
        view = EventListView(
            self.view.display, self.model, self.event_loop, Config.side_view_width,
            self.view.display.get_height() - Config.appbar_height, 0, 0, event.date
        )
        EventListController(self.view.model, view, self.event_loop)
        view.event_to_highlight = event
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, False))
