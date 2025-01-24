from typing import Union

import pygame
import pygame.gfxdraw

from src.events.event import Event
from src.main.settings import Settings
from src.ui.colors import Colors
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.rendering import render_rounded_rect


class IndependentLabel(UIObject):

    def __init__(self, display: pygame.Surface, label: Label, width: int, height: int, x: int, y: int) -> None:
        super().__init__(display, (x, y), Padding())
        self.display = display
        self.label = label
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.shadow_canvas = pygame.Surface((self.width + 8, self.height + 8), pygame.SRCALPHA)
        
        self.label.post_init(self.canvas, (self.width // 2 + 9, self.height // 2), (self.width - 18, self.height))

    def register_event(self, event: Event) -> bool:
        pass

    def render(self) -> None:
        self.canvas.fill((0, 0, 0, 0))

        pygame.gfxdraw.filled_polygon(self.canvas, self.get_triangle(), Colors.BACKGROUND_GREY22)
        pygame.gfxdraw.aapolygon(self.canvas, self.get_triangle(), (100, 100, 100))
        pygame.gfxdraw.aapolygon(self.canvas, self.get_triangle(), (100, 100, 100))
        pygame.gfxdraw.aapolygon(self.canvas, self.get_triangle(), Colors.GREY70)
        pygame.gfxdraw.filled_polygon(self.canvas, [(0, self.height // 2), (10, self.height // 4 + 1), (10, self.height * 3 // 4 - 1)], Colors.BACKGROUND_GREY22)

        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY22, self.get_rect(), border_radius=4)
        if Settings().get_settings()["high_quality_graphics"]:
            render_rounded_rect(self.canvas, Colors.GREY70, self.get_rect(), 4, width=1)
        else:
            pygame.draw.rect(self.canvas, Colors.GREY70, self.get_rect(), width=1, border_radius=4)

        pygame.draw.line(self.canvas, Colors.BACKGROUND_GREY22, (10, self.height // 4 + 1), (10, self.height // 4 * 3))

        self.label.render()

        self.shadow_canvas.fill((0, 0, 0, 0))
        for i in range(8):
            pygame.draw.rect(self.shadow_canvas, (0, 0, 0, max(70 - i * 9, 0)),
                             (self.get_rect().x, 0, self.get_rect().w + i, self.get_rect().h + i),
                             border_radius=4 + 2 * i, width=2)

        self.display.blit(self.shadow_canvas, (self.x, self.y))
        self.display.blit(self.canvas, (self.x, self.y))

    def update_canvas(self, display: pygame.Surface) -> None:
        self.display = display

    def get_triangle(self) -> list[tuple[int, int]]:
        return [(0, self.height // 2), (10, self.height // 4), (10, self.height * 3 // 4)]

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(10, 0, self.width - 10, self.height)
