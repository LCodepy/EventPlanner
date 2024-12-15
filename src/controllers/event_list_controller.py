import time
from typing import Union

import pygame

from src.controllers.add_event_controller import AddEventController
from src.events.event import MouseClickEvent, MouseReleaseEvent, MouseMotionEvent, ResizeViewEvent, MouseWheelUpEvent, \
    MouseWheelDownEvent, OpenViewEvent, AddCalendarEventEvent, CloseViewEvent, UpdateCalendarEvent
from src.events.event_loop import EventLoop
from src.models.calendar_model import CalendarModel, CalendarEvent
from src.views.add_event_view import AddEventView
from src.views.event_list_view import EventListView


class EventListController:

    def __init__(self, model: CalendarModel, view: EventListView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.pressed = False
        self.last_frame_interacted = False
        self.scroll_value = 10
        self.add_event_view = None

        self.view.add_event_button.bind_on_click(self.open_add_event_view)
        self.view.bind_on_click(self.on_click)
        self.view.bind_on_release(self.on_release)
        self.view.bind_on_mouse_motion(self.on_mouse_motion)
        self.view.bind_on_scroll(self.on_scroll)
        self.view.bind_on_resize(self.on_resize)
        self.view.bind_add_event(self.add_event)
        self.view.bind_event_methods(self.delete_event)

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
            return True

    def on_scroll(self, event: Union[MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        if event.x < 0 or event.x > self.view.width or event.y < 0 or event.y > self.view.height:
            return False

        if isinstance(event, MouseWheelUpEvent):
            pass
        elif isinstance(event, MouseWheelDownEvent):
            pass

    def on_resize(self) -> None:
        self.view.bind_event_methods(self.delete_event)

    def delete_event(self, event: CalendarEvent) -> None:
        self.model.remove_event(event)
        for events in self.view.time_table.values():
            r = False
            for i in range(len(events)):
                if events[i] == event:
                    r = True
                    break
            if r:
                events.pop(i)

        self.view.create_time_table()
        self.view.bind_event_methods(self.delete_event)
        self.event_loop.enqueue_event(UpdateCalendarEvent(time.time()))

    def open_add_event_view(self) -> None:
        self.add_event_view = AddEventView(
            self.view.display, self.event_loop, 400, 500,
            self.view.display.get_width() // 2 - 200, self.view.display.get_height() // 2 - 250
        )
        AddEventController(self.add_event_view, self.event_loop)

        self.event_loop.enqueue_event(
            OpenViewEvent(time.time(), self.add_event_view, True)
        )

    def add_event(self, ev: AddCalendarEventEvent) -> None:
        event = CalendarEvent(self.view.date, ev.time, ev.description, ev.color, ev.is_recurring)
        self.model.add_event(event)
        self.view.create_time_table()
        self.view.bind_event_methods(self.delete_event)
        self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.add_event_view))
        self.event_loop.enqueue_event(UpdateCalendarEvent(time.time()))
