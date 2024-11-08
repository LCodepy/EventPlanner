from typing import Callable

import pygame

from src.events.event import Event, MouseMotionEvent, MouseReleaseEvent, MouseClickEvent, MouseFocusChangedEvent, \
    WindowMinimizedEvent, WindowUnminimizedEvent
from src.events.mouse_buttons import MouseButtons
from src.ui.colors import Color, Colors, brighten
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.ui_debugger import UIDebugger


class Button(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), label: Label = None,
                 color: Color = Colors.WHITE, border_color: Color = Colors.BLACK, border_radius: int = 0,
                 border_width: int = 1, apply_hover_effects: bool = True, hover_color: Color = None,
                 click_color: Color = None, image: pygame.Surface = None, hover_image: pygame.Surface = None,
                 padding: Padding = None) -> None:
        super().__init__(canvas, pos, padding)
        self.canvas = canvas
        self.x, self.y = pos
        self.width, self.height = size

        self.label = label
        self.color = color
        self.border_color = border_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.apply_hover_effects = apply_hover_effects
        self.hover_color = hover_color or brighten(self.color, 20)
        self.click_color = click_color or brighten(self.color, 30)
        self.image = image
        self.hover_image = hover_image
        self.padding = padding or Padding()

        self.render_color = self.color[:]

        if self.label:
            self.label.post_init(self.canvas, pos, size)
            self.label.x += self.padding.left - self.padding.right
            self.label.y += self.padding.top - self.padding.bottom

        if self.image:
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        if self.hover_image:
            self.hover_image = pygame.transform.scale(self.hover_image, (self.width, self.height))

        self.hovering = False
        self.pressed = False

        self.on_click_bind = None
        self.on_enter_bind = None
        self.on_exit_bind = None

    def register_event(self, event: Event) -> bool:
        if isinstance(event, MouseMotionEvent):
            currently_hovering = self.is_hovering((event.x, event.y))
            if currently_hovering != self.hovering:
                if self.hovering:
                    self.on_exit()
                else:
                    self.on_enter()
                self.hovering = currently_hovering
                return True
        elif isinstance(event, MouseFocusChangedEvent):
            if self.hovering and not event.focused:
                self.hovering = event.focused
                self.on_exit()
                return True
        elif isinstance(event, WindowMinimizedEvent):
            self.hovering = False
            self.on_exit()
            return True
        elif isinstance(event, WindowUnminimizedEvent):
            return True
        elif (
            isinstance(event, MouseClickEvent) and
            self.is_hovering((event.x, event.y)) and
            event.button is MouseButtons.LEFT_BUTTON
        ):
            self.pressed = True
            self.on_click()
            return True
        elif (
            isinstance(event, MouseReleaseEvent) and
            self.is_hovering((event.x, event.y)) and
            event.button is MouseButtons.LEFT_BUTTON and
            self.pressed
        ):
            self.pressed = False
            self.on_release()
            return True

        if self.label is not None and self.label.register_event(event):
            return True
        return False

    def render(self) -> None:
        pygame.draw.rect(self.canvas, self.render_color, self.get_rect(), border_radius=self.border_radius)
        if self.border_width:
            pygame.draw.rect(
                self.canvas, self.border_color, self.get_rect(), width=self.border_width, border_radius=self.border_radius
            )
        if self.hover_image and self.hovering:
            self.canvas.blit(self.hover_image, self.get_rect().topleft)
        elif self.image:
            self.canvas.blit(self.image, self.get_rect().topleft)

        if self.label is not None:
            self.label.render()

        # UI debugging
        if UIDebugger.is_enabled():
            pygame.draw.rect(self.canvas, UIDebugger.box_color, self.get_rect(), 1)
            pygame.draw.circle(self.canvas, UIDebugger.center_point_color, (self.x, self.y), 2)

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        if self.label:
            self.label.update_canvas(self.canvas)

    def update_position(self, x: int = None, y: int = None) -> None:
        if self.label:
            self.label.x -= (self.x - (x or self.x))
            self.label.y -= (self.y - (y or self.y))
        self.x = x or self.x
        self.y = y or self.y

    def on_click(self) -> None:
        if self.apply_hover_effects:
            self.render_color = self.click_color or brighten(self.color, 50)

    def on_release(self) -> None:
        if self.apply_hover_effects:
            self.render_color = self.hover_color[:]
        if self.on_click_bind is not None:
            self.on_click_bind()

    def on_enter(self) -> None:
        if self.apply_hover_effects:
            self.render_color = self.hover_color
        if self.on_enter_bind is not None:
            self.on_enter_bind()

    def on_exit(self) -> None:
        if self.apply_hover_effects:
            self.render_color = self.color[:]
        if self.on_exit_bind is not None:
            self.on_exit_bind()

    def bind_on_click(self, on_click: Callable) -> None:
        self.on_click_bind = on_click

    def bind_on_enter(self, on_enter: Callable) -> None:
        self.on_enter_bind = on_enter

    def bind_on_exit(self, on_exit: Callable) -> None:
        self.on_exit_bind = on_exit

    def is_hovering(self, mouse_pos) -> bool:
        mouse_x, mouse_y = mouse_pos
        if self.border_radius:
            left_center_x = self.x - self.width // 2 + self.border_radius
            right_center_x = self.x + self.width // 2 - self.border_radius
            top_center_y = self.y - self.height // 2 + self.border_radius
            bottom_center_y = self.y + self.height // 2 - self.border_radius
            if mouse_x < left_center_x:
                if mouse_y < top_center_y and \
                        (left_center_x - mouse_x) ** 2 + (top_center_y - mouse_y) ** 2 > self.border_radius ** 2:
                    return False
                elif mouse_y > bottom_center_y and \
                        (left_center_x - mouse_x) ** 2 + (bottom_center_y - mouse_y) ** 2 > self.border_radius ** 2:
                    return False
            elif mouse_x > right_center_x:
                if mouse_y < top_center_y and \
                        (right_center_x - mouse_x) ** 2 + (top_center_y - mouse_y) ** 2 > self.border_radius ** 2:
                    return False
                elif mouse_y > bottom_center_y and \
                        (right_center_x - mouse_x) ** 2 + (bottom_center_y - mouse_y) ** 2 > self.border_radius ** 2:
                    return False

        return self.get_rect().collidepoint(mouse_x, mouse_y)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)



