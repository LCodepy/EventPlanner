import time
from typing import Callable

from src.events.event import Event, EventFactory
from src.events.event_loop import EventLoop
from src.main.config import Config


class ChangeValuesAnimation:

    def __init__(self, name: str, event_loop: EventLoop, animation_time: float = None, fps: int = Config().fps) -> None:
        self.name = name
        self.event_loop = event_loop
        self.animation_time = animation_time
        self.fps = fps

        self.type = EventFactory.create_custom_event(self.name)

        self.active = False
        self.values = None
        self.start_values = None
        self.end_values = None
        self.start_time = None
        self.frames = None

        self.on_stop = None

    def start(self, start_values: list[float], end_values: list[float], animation_time: float = None) -> None:
        if self.active:
            self.event_loop.remove_repeating_event(self.type)
        self.active = True
        self.start_values = start_values
        self.end_values = end_values
        self.animation_time = animation_time or self.animation_time

        self.frames = self.calculate_frames()
        self.start_time = time.time()
        self.event_loop.add_repeating_event(self.type, 1 / self.fps)

    def stop(self) -> None:
        self.active = False
        self.values = None
        self.start_values = None
        self.start_time = None
        self.frames = None
        self.event_loop.remove_repeating_event(self.type)

        self.values = self.end_values

        if self.on_stop:
            self.on_stop()

    def calculate_frames(self) -> list[list[float]]:
        n_frames = int(self.fps * self.animation_time)
        frames = [[] for _ in range(n_frames)]
        for frame in range(n_frames):
            for i in range(len(self.start_values)):
                frames[frame].append(self.start_values[i] + (self.end_values[i] - self.start_values[i]) / n_frames * frame)
        return frames

    def register_event(self, event: Event) -> bool:
        if not self.active:
            return False

        if time.time() - self.start_time >= self.animation_time:
            self.stop()
            return True
        if isinstance(event, self.type):
            self.set_values()
            return True

    def set_values(self) -> None:
        n_frames = self.fps * self.animation_time
        current_frame = int((time.time() - self.start_time) / self.animation_time * n_frames)
        self.values = self.frames[current_frame]

    def bind_on_stop(self, on_stop: Callable) -> None:
        self.on_stop = on_stop
