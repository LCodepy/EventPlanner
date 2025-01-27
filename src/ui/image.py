import pygame
import pygame.gfxdraw

from src.events.event import Event, MouseMotionEvent, MouseFocusChangedEvent, MouseClickEvent, MouseReleaseEvent, \
    WindowMinimizedEvent, WindowUnminimizedEvent
from src.events.mouse_buttons import MouseButtons
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.ui_debugger import UIDebugger


class Image(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), image: pygame.Surface, size: (int, int) = None,
                 hover_image: pygame.Surface = None, border_radius: int = None, padding: Padding = None) -> None:
        super().__init__(canvas, pos, padding)
        self.canvas = canvas
        self.x, self.y = pos
        self.image = image
        self.hover_image = hover_image
        self.border_radius = border_radius
        self.padding = padding or Padding()

        self.width, self.height = size or self.image.get_rect().size

        if self.image:
            self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))
        if self.hover_image:
            self.hover_image = pygame.transform.smoothscale(self.hover_image, (self.width, self.height))

        self.hovering = False
        self.pressed = False

    def register_event(self, event: Event) -> bool:
        if isinstance(event, MouseMotionEvent):
            currently_hovering = self.is_hovering((event.x, event.y))
            if currently_hovering != self.hovering:
                self.hovering = currently_hovering
                return True
        elif isinstance(event, MouseFocusChangedEvent):
            if self.hovering and not event.focused:
                self.hovering = event.focused
                return True
        elif isinstance(event, WindowMinimizedEvent):
            self.hovering = False
            return True
        elif isinstance(event, WindowUnminimizedEvent):
            return True
        elif (
                isinstance(event, MouseClickEvent) and
                self.is_hovering((event.x, event.y)) and
                event.button is MouseButtons.LEFT_BUTTON
        ):
            self.pressed = True
            return True
        elif (
                isinstance(event, MouseReleaseEvent) and
                self.is_hovering((event.x, event.y)) and
                event.button is MouseButtons.LEFT_BUTTON
        ):
            self.pressed = False
            return True

    def render(self) -> None:
        if self.border_radius:
            mask = pygame.Surface((self.width * 10, self.height * 10), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.rect(
                mask, (255, 255, 255, 255), [0, 0, self.width * 10, self.height * 10],
                border_radius=self.border_radius * 10
            )
            mask = pygame.transform.smoothscale(mask, (self.width, self.height))

            if self.hover_image and self.hovering:
                self.hover_image.set_colorkey((0, 0, 0))
                masked_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                masked_surface.blit(self.hover_image, (0, 0))
                masked_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.canvas.blit(masked_surface, self.get_rect().topleft)
            else:
                self.image.set_colorkey((0, 0, 0))
                masked_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                masked_surface.blit(self.image, (0, 0))
                masked_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.canvas.blit(masked_surface, self.get_rect().topleft)

        elif self.hover_image and self.hovering:
            self.canvas.blit(self.hover_image, self.get_rect().topleft)
        else:
            self.canvas.blit(self.image, self.get_rect().topleft)

        if UIDebugger.is_enabled():
            pygame.draw.rect(self.canvas, UIDebugger.box_color, self.get_rect(), 1)
            pygame.draw.circle(self.canvas, UIDebugger.center_point_color, (self.x, self.y), 2)

    def set_image(self, img: pygame.Surface) -> None:
        self.image = pygame.transform.scale(img, (self.width, self.height))

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas

    def is_hovering(self, mouse_pos) -> bool:
        return self.get_rect().collidepoint(*mouse_pos)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
