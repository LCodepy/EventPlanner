import time

import pygame

from src.events.event import Event, MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, KeyReleaseEvent, \
    KeyPressEvent, RenderCursorEvent, DeleteCharacterEvent, MouseFocusChangedEvent, WindowMinimizedEvent, \
    WindowUnminimizedEvent
from src.events.mouse_buttons import MouseButtons
from src.ui.colors import Color, Colors, darken, brighten
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.logging import Log
from src.utils.ui_debugger import UIDebugger


class TextField(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), label: Label = None, hint: str = "",
                 color: Color = Colors.WHITE, border_color: Color = Colors.BLACK, border_radius: int = 0,
                 border_width: int = 1, max_length: int = None, hint_text_color: Color = None,
                 padding: Padding = None) -> None:
        super().__init__(canvas, pos, padding)
        self.canvas = canvas
        self.x, self.y = pos
        self.width, self.height = size

        self.label = label or Label(canvas, pos, size, text=hint, text_color=Colors.BLACK,
                                    font=pygame.font.SysFont("arial", 14))
        self.hint = hint
        self.color = color
        self.border_color = border_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.max_length = max_length
        self.padding = padding or Padding()
        self.hint_text_color = hint_text_color or brighten(self.label.text_color, 50)

        self.text = ""

        self.text_color = self.label.text_color
        self.label.post_init(self.canvas, pos, size)
        self.label.set_text(self.hint)
        self.label.text_color = self.hint_text_color
        self.label.x += self.padding.left - self.padding.right
        self.label.y += self.padding.top - self.padding.bottom

        self.hovering = False
        self.focused = False

        self.render_cursor = False

        self.backspace_pressed = False
        self.backspace_pressed_time = None
        self.last_backspace_time = 0
        self.initiate_deleting_time = 0.4

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
        elif isinstance(event, WindowMinimizedEvent):
            self.hovering = False
            self.on_exit()
            return True
        elif isinstance(event, WindowUnminimizedEvent):
            return True
        elif isinstance(event, MouseFocusChangedEvent):
            if self.hovering:
                self.hovering = event.focused
                self.on_exit()
                return True
        elif (
                isinstance(event, MouseClickEvent) and
                event.button is MouseButtons.LEFT_BUTTON and
                self.is_hovering((event.x, event.y))
        ):
            self.on_click()
            return True
        elif (
                isinstance(event, MouseReleaseEvent) and
                event.button is MouseButtons.LEFT_BUTTON and
                self.is_hovering((event.x, event.y))
        ):
            self.on_release(event)
            return True
        elif isinstance(event, KeyReleaseEvent) and self.focused:
            self.update_text(event.keycode, event.unicode)
            return True
        elif isinstance(event, KeyPressEvent) and self.focused:
            self.update_text_on_press(event.keycode, event.unicode)
            return True
        elif isinstance(event, RenderCursorEvent) and self.focused:
            self.render_cursor = not self.render_cursor
            return True
        elif isinstance(event, DeleteCharacterEvent) and self.focused and self.backspace_pressed:
            if time.time() - self.backspace_pressed_time > self.initiate_deleting_time:
                self.text = self.text[:-1]
                self.label.set_text(self.text)
            return True

        if self.label is not None and self.label.register_event(event):
            return True
        return False

    def update_text(self, keycode: int, unicode: str) -> None:
        self.label.text_color = self.text_color
        if keycode == pygame.K_RETURN:
            self.text += "\n"
        elif keycode == pygame.K_SPACE:
            self.text += " "
        elif keycode == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            self.backspace_pressed = False
            self.backspace_pressed_time = None
        elif unicode:
            self.text += unicode

        self.label.set_text(self.text)

    def update_text_on_press(self, keycode: int, unicode: str) -> None:
        if keycode == pygame.K_BACKSPACE:
            self.backspace_pressed = True
            self.backspace_pressed_time = time.time()
        else:
            self.backspace_pressed = False
            self.backspace_pressed_time = None

    def render(self) -> None:
        pygame.draw.rect(self.canvas, self.color, self.get_rect(), border_radius=self.border_radius)
        if self.border_width:
            pygame.draw.rect(
                self.canvas, self.border_color, self.get_rect(),
                width=self.border_width, border_radius=self.border_radius
            )
        if self.label is not None:
            self.label.render()

        if self.render_cursor and self.focused:
            end_x, end_y = self.label.get_text_end_pos()
            text_height = self.label.get_text_height()
            end_x = end_x or 0
            end_y = end_y or 0

            pygame.draw.line(self.canvas, self.text_color, (end_x, end_y), (end_x, end_y + text_height), 2)

        # UI debugging
        if UIDebugger.is_enabled():
            pygame.draw.rect(self.canvas, UIDebugger.box_color, self.get_rect(), 1)
            pygame.draw.circle(self.canvas, UIDebugger.center_point_color, (self.x, self.y), 2)

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.label.update_canvas(self.canvas)

    def update_position(self, x: int = None, y: int = None) -> None:
        self.label.x += (self.x - (x or self.x))
        self.label.y += (self.y - (y or self.y))
        self.x = x or self.x
        self.y = y or self.y

    def on_click(self) -> None:
        pass

    def on_release(self, event: MouseReleaseEvent) -> None:
        if self.is_hovering((event.x, event.y)):
            self.focused = True
            if not self.text:
                self.label.set_text("")
        else:
            self.focused = False
            if not self.text:
                self.label.set_text(self.hint)
                self.label.text_color = self.hint_text_color

    def on_exit(self) -> None:
        pass

    def on_enter(self) -> None:
        pass

    def is_hovering(self, mouse_pos) -> bool:
        return self.get_rect().collidepoint(*mouse_pos)

    def is_deleting_initiated(self) -> bool:
        return self.backspace_pressed_time and time.time() - self.backspace_pressed_time > self.initiate_deleting_time

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
