import time
from dataclasses import dataclass

import pygame

from src.events.event import CloseWindowEvent, MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, \
    MouseWheelDownEvent, MouseMotionEvent, Event, KeyPressEvent, KeyReleaseEvent, MouseFocusChangedEvent, \
    WindowUnminimizedEvent, WindowMinimizedEvent, TimerEvent, UserSignInEvent, ThreadedEvent
from src.events.mouse_buttons import MouseButtons
from src.events.queue import EventQueue


@dataclass
class RepeatingEvent:

    event: type
    timer: float
    last_queued: float = 0


class EventLoop:

    def __init__(self) -> None:
        self.event_queue = EventQueue()
        self.threaded_events: list[ThreadedEvent] = []
        self.repeating_events: list[RepeatingEvent] = []
        self.timer_events: list[TimerEvent] = []
        self.mouse_focused = False

    def run(self) -> None:
        current_time = time.time()

        self.clear_threaded_events()
        self.event_queue.clear()

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.event_queue.add(CloseWindowEvent(current_time))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    button = MouseButtons.LEFT_BUTTON
                elif event.button == 2:
                    button = MouseButtons.SCROLL_WHEEL
                elif event.button == 3:
                    button = MouseButtons.RIGHT_BUTTON
                else:
                    button = MouseButtons.UNKNOWN
                self.event_queue.add(MouseClickEvent(current_time, mouse_x, mouse_y, button))
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    button = MouseButtons.LEFT_BUTTON
                elif event.button == 2:
                    button = MouseButtons.SCROLL_WHEEL
                elif event.button == 3:
                    button = MouseButtons.RIGHT_BUTTON
                else:
                    button = MouseButtons.UNKNOWN
                self.event_queue.add(MouseReleaseEvent(current_time, mouse_x, mouse_y, button))
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.event_queue.add(MouseWheelUpEvent(current_time, mouse_x, mouse_y, event.dict["precise_y"]))
                elif event.y < 0:
                    self.event_queue.add(MouseWheelDownEvent(current_time, mouse_x, mouse_y, event.dict["precise_y"]))
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                xr, yr = event.rel
                self.event_queue.add(MouseMotionEvent(current_time, x - xr, y - yr, x, y))
            elif event.type == pygame.KEYDOWN:
                self.event_queue.add(KeyPressEvent(current_time, event.key, event.unicode))
            elif event.type == pygame.KEYUP:
                self.event_queue.add(KeyReleaseEvent(current_time, event.key, event.unicode))
            elif event.type == pygame.ACTIVEEVENT:
                if event.gain:
                    self.event_queue.add(WindowUnminimizedEvent(current_time))
                else:
                    self.event_queue.add(WindowMinimizedEvent(current_time))

        if pygame.mouse.get_focused() != self.mouse_focused:
            self.mouse_focused = not self.mouse_focused
            self.event_queue.add(MouseFocusChangedEvent(current_time, self.mouse_focused))

        for r_event in self.repeating_events:
            if current_time - r_event.last_queued > r_event.timer:
                r_event.last_queued = current_time
                self.event_queue.add(r_event.event(current_time))

        timers_to_remove = []
        for event in self.timer_events:
            if time.time() - event.exec_time >= event.duration:
                event.callback()
                timers_to_remove.append(event)

        for event in timers_to_remove:
            self.timer_events.remove(event)

        for event in self.threaded_events:
            event.registered = True
            self.event_queue.add(event)

    def clear_threaded_events(self) -> None:
        to_remove = []
        for event in self.threaded_events:
            if event.registered:
                to_remove.append(event)

        for event in to_remove:
            self.threaded_events.remove(event)

    def add_repeating_event(self, event: type, timer: float) -> None:
        if not issubclass(event, Event):
            return
        self.repeating_events.append(RepeatingEvent(event, timer, time.time()))

    def remove_repeating_event(self, event: type) -> None:
        idx = None
        for idx, ev in enumerate(self.repeating_events):
            if type(ev.event) == event:
                break

        if idx is not None:
            self.repeating_events.pop(idx)

    def enqueue_event(self, event: Event) -> None:
        if isinstance(event, TimerEvent):
            self.timer_events.append(event)
            return

        self.event_queue.add(event)

    def enqueue_threaded_event(self, event: ThreadedEvent) -> None:
        self.threaded_events.append(event)

    def next(self) -> Event:
        return self.event_queue.get()

    def has_events(self) -> bool:
        return self.event_queue.is_empty()


