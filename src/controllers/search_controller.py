import time

import pygame

from src.controllers.event_list_controller import EventListController
from src.events.event import MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, ResizeViewEvent, OpenViewEvent
from src.events.event_loop import EventLoop
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
                ResizeViewEvent(time.time(), self.view, min(max(event.x, self.view.get_min_size()[0]), 550))
            )
            self.view.search_bar.set_focus(False)
            return True

    def on_search_bar_typed(self) -> None:
        query = self.view.search_bar.text

        search_results = []
        if query:
            search_results = self.model.search_events(query)

        self.view.create_search_events(search_results)
        self.view.bind_search_event_methods()

    def on_search_event_release(self, event: CalendarEvent) -> None:
        view = EventListView(
            self.view.display, self.model, self.event_loop, 300, self.view.display.get_height() - 30, 0, 0, event.date
        )
        EventListController(self.view.model, view, self.event_loop)
        view.event_to_highlight = event
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, False))

