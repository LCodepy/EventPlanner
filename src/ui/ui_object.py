from abc import ABC, abstractmethod

import pygame

from src.events.event import Event
from src.ui.padding import Padding


class UIObject(ABC):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), padding: Padding = None) -> None:
        self.canvas = canvas
        self.x, self.y = pos
        self.padding = padding

    @abstractmethod
    def register_event(self, event: Event) -> bool:
        """Updates the element according to the event."""

    @abstractmethod
    def render(self) -> None:
        """Renders the UI object."""

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas

