import string
import time
from typing import Callable

import pygame

from src.events.event import Event, MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, KeyReleaseEvent, \
    KeyPressEvent, RenderCursorEvent, DeleteCharacterEvent, MouseFocusChangedEvent, WindowMinimizedEvent, \
    WindowUnminimizedEvent
from src.events.mouse_buttons import MouseButtons
from src.main.settings import Settings
from src.ui.colors import Color, Colors, darken, brighten
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.logging import Log
from src.utils.rendering import render_rounded_rect
from src.utils.ui_debugger import UIDebugger


class TextField(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), label: Label = None, hint: str = "",
                 color: Color = Colors.WHITE, border_color: Color = Colors.BLACK, border_radius: int = 0,
                 border_width: int = 1, max_length: int = None, hint_text_color: Color = None,
                 allowed_char_set: set[str] = None, underline: Color = None,
                 oneline: bool = False, padding: Padding = None) -> None:
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
        self.max_length = max_length or float("inf")
        self.allowed_char_set = allowed_char_set or self.create_allowed_charset()
        self.underline = underline
        self.oneline = oneline
        self.padding = padding or Padding()
        self.hint_text_color = hint_text_color or brighten(self.label.text_color, 50)

        self.text = ""

        self.text_color = self.label.text_color
        self.label.count_start_line = 1
        self.label.post_init(self.canvas, pos, (size[0] - self.padding.left - self.padding.right,
                                                size[1] - self.padding.top - self.padding.bottom))
        self.label.oneline = oneline
        self.label.set_text(self.hint)
        self.label.text_color = self.hint_text_color
        self.label.x += self.padding.left - self.padding.right
        self.label.y += self.padding.top - self.padding.bottom

        self.hovering = False
        self.focused = False

        self.on_enter = lambda: None
        self.on_exit = lambda: None
        self.on_key = lambda: None
        self.on_focus_changed = lambda _: None

        self.render_cursor = False
        self.cursor_pos = -1
        self.label_offsets = []

        self.backspace_pressed = False
        self.backspace_pressed_time = None
        self.last_backspace_time = 0
        self.initiate_deleting_time = 0.4

        self.delete_pressed = False
        self.delete_pressed_time = None
        self.last_delete_time = 0

        self.arrow_pressed = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False}
        self.arrow_pressed_time = None
        self.last_arrow_time = 0
        self.initiate_arrow_time = 0.4

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
                event.button is MouseButtons.LEFT_BUTTON
        ):
            self.on_release(event)
            return True
        elif isinstance(event, KeyReleaseEvent) and self.focused:
            self.update_text(event.keycode, event.unicode)
            self.on_key()
            return True
        elif isinstance(event, KeyPressEvent) and self.focused:
            self.update_text_on_press(event.keycode, event.unicode)
            self.on_key()
            return True
        elif isinstance(event, RenderCursorEvent) and self.focused:
            self.render_cursor = not self.render_cursor
            return True
        elif isinstance(event, DeleteCharacterEvent) and self.focused:
            if self.backspace_pressed and time.time() - self.backspace_pressed_time > self.initiate_deleting_time:
                self.delete_char()
            elif self.delete_pressed and time.time() - self.delete_pressed_time > self.initiate_deleting_time:
                self.delete_next_char()
            elif self.arrow_pressed_time and time.time() - self.arrow_pressed_time > self.initiate_arrow_time:
                if self.arrow_pressed[pygame.K_LEFT] and self.cursor_pos >= 0:
                    self.move_cursor(-1)
                elif self.arrow_pressed[pygame.K_RIGHT] and self.cursor_pos < len(self.text) - 1:
                    self.move_cursor(1)
                elif self.arrow_pressed[pygame.K_UP]:
                    self.move_cursor_up_down(-1)
                elif self.arrow_pressed[pygame.K_DOWN]:
                    self.move_cursor_up_down(1)
            return True

        if self.label is not None and self.label.register_event(event):
            return True

        return False

    def update_text(self, keycode: int, unicode: str) -> None:
        self.label.text_color = self.text_color

        if keycode == pygame.K_LEFT:
            self.arrow_pressed[pygame.K_LEFT] = False
        elif keycode == pygame.K_RIGHT:
            self.arrow_pressed[pygame.K_RIGHT] = False
        elif keycode == pygame.K_UP:
            self.arrow_pressed[pygame.K_UP] = False
        elif keycode == pygame.K_DOWN:
            self.arrow_pressed[pygame.K_DOWN] = False

        if keycode == pygame.K_BACKSPACE:
            self.delete_char()
            self.backspace_pressed = False
            self.backspace_pressed_time = None
        elif keycode == pygame.K_DELETE:
            self.delete_next_char()
            self.delete_pressed = False
            self.delete_pressed_time = None

        if len(self.text) >= self.max_length:
            return

        if keycode == pygame.K_RETURN and not self.oneline:
            self.add_char("\n")
            if len(self.label.lines) * (self.label.get_text_height() + self.label.line_spacing) > self.label.height and \
                    self.label.get_char_pos(self.cursor_pos)[1] < self.label.y + self.label.height // 2 - self.label.get_text_height() - self.label.line_spacing:
                self.label.y_offset += self.label.get_text_height() + self.label.line_spacing
        elif keycode == pygame.K_SPACE and " " in self.allowed_char_set:
            self.add_char(" ")
        elif unicode and unicode in self.allowed_char_set and keycode != pygame.K_RETURN:
            self.add_char(unicode)

        self.label.set_text(self.text)

    def update_text_on_press(self, keycode: int, unicode: str) -> None:
        if keycode == pygame.K_BACKSPACE:
            self.backspace_pressed = True
            self.backspace_pressed_time = time.time()
        else:
            self.backspace_pressed = False
            self.backspace_pressed_time = None

        if keycode == pygame.K_DELETE:
            self.delete_pressed = True
            self.delete_pressed_time = time.time()
        else:
            self.delete_pressed = False
            self.delete_pressed_time = None

        if keycode == pygame.K_LEFT and self.cursor_pos >= 0:
            self.move_cursor(-1)
            self.arrow_pressed[pygame.K_LEFT] = True
            self.arrow_pressed_time = time.time()
            return
        else:
            self.arrow_pressed[pygame.K_LEFT] = False
            self.arrow_pressed_time = None

        if keycode == pygame.K_RIGHT and self.cursor_pos < len(self.text) - 1:
            self.move_cursor(1)
            self.arrow_pressed[pygame.K_RIGHT] = True
            self.arrow_pressed_time = time.time()
            return
        else:
            self.arrow_pressed[pygame.K_RIGHT] = False
            self.arrow_pressed_time = None

        if keycode == pygame.K_UP:
            self.move_cursor_up_down(-1)
            self.arrow_pressed[pygame.K_UP] = True
            self.arrow_pressed_time = time.time()
            return
        else:
            self.arrow_pressed[pygame.K_UP] = False
            self.arrow_pressed_time = None

        if keycode == pygame.K_DOWN:
            self.move_cursor_up_down(1)
            self.arrow_pressed[pygame.K_DOWN] = True
            self.arrow_pressed_time = time.time()
            return
        else:
            self.arrow_pressed[pygame.K_DOWN] = False
            self.arrow_pressed_time = None

    def delete_char(self) -> None:
        if self.cursor_pos >= 0 and self.text[self.cursor_pos] == "\n" and self.label.y_offset > 0:
            self.label.y_offset -= self.label.get_text_height() + self.label.line_spacing

        if self.cursor_pos == len(self.text) - 1:
            self.text = self.text[:-1]
        elif self.cursor_pos == 0 and len(self.label.lines[0]) == 1:
            self.text = self.text[self.cursor_pos + 1:]
            self.label.y_offset -= self.label.get_text_height() + self.label.line_spacing
        elif self.cursor_pos != -1:
            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]

        self.label.set_text(self.text)
        self.move_cursor(-1, delete=True)

    def delete_next_char(self) -> None:
        if self.cursor_pos < len(self.text) - 1:
            self.text = self.text[:self.cursor_pos + 1] + self.text[self.cursor_pos + 2:]

        if self.cursor_pos + 1 < len(self.label.text) and self.label.text[self.cursor_pos + 1] == "\n" and self.label.y_offset > 0:
            self.label.y_offset -= self.label.get_text_height() + self.label.line_spacing

        self.label.set_text(self.text)

    def add_char(self, char: str) -> None:
        self.text = self.text[:self.cursor_pos+1] + char + self.text[self.cursor_pos+1:]
        self.label.set_text(self.text)
        self.move_cursor(1)

    def move_cursor(self, direction: int, delete: bool = False) -> None:
        self.cursor_pos = max(min(self.cursor_pos + direction, len(self.text)-1), -1)

        if not self.oneline:
            char_pos = self.label.get_char_pos(self.cursor_pos)[1]

            if direction < 0 and char_pos < self.label.y - self.label.height // 2:
                self.label.y_offset += self.label.get_text_height() + self.label.line_spacing
            elif direction > 0 and char_pos + self.label.get_text_height() > self.label.y + self.label.height // 2:
                self.label.y_offset -= self.label.get_text_height() + self.label.line_spacing
            return

        char_pos = self.label.get_char_pos(self.cursor_pos)[0] + self.label.width // 2 - self.label.x
        char_pos0 = self.label.get_char_pos(-1)[0] + self.label.width // 2 - self.label.x
        diff = self.label.width - char_pos

        if direction > 0 and char_pos > self.label.width:
            self.label.x_offset += diff
            self.label_offsets.append(diff)
        elif direction < 0 and char_pos0 < 0 and delete:
            self.label.x_offset -= self.label_offsets.pop()
        elif direction < 0 and char_pos < 0 and not delete:
            self.label.x_offset -= char_pos
            self.label_offsets.append(-char_pos)

    def move_cursor_up_down(self, direction: int) -> None:
        if (direction < 0 and self.cursor_pos < 0) or (direction > 0 and self.cursor_pos >= len(self.text) - 1) or self.oneline:
            return

        line = 0
        char_count = 0
        char_count2 = 1
        char_pos = 0

        for i in range(len(self.label.lines)):
            line = i
            char_count = 0
            for _ in self.label.lines[line]:
                if char_pos <= self.cursor_pos:
                    char_count += 1
                else:
                    char_count2 += 1

                char_pos += 1

            if char_pos > self.cursor_pos:
                break

        if direction > 0:
            if line >= len(self.label.lines) - 1:
                return
            new_line = line+1
            char_count2 += len(self.label.lines[new_line]) - 1
        else:
            if line < 1:
                return
            new_line = line - 1

        change = -char_count
        if direction > 0:
            change = char_count2

        x, y = self.label.get_char_pos(self.cursor_pos)
        closest = self.label.get_closest_character(
            x, y + (self.label.get_text_height() + self.label.line_spacing) * direction
        )

        char_count3 = -1
        char_pos = self.cursor_pos + change - len(self.label.lines[new_line]) + 1
        for _ in self.label.lines[new_line]:
            if char_pos >= closest:
                char_count3 += 1
            char_pos += 1

        if not self.label.lines[new_line]:
            char_count3 = 0

        change -= char_count3

        if direction < 0 and line >= 1:
            self.move_cursor(change)
        elif direction > 0 and line < len(self.label.lines) - 1:
            self.move_cursor(change)

    def get_relative_char_pos(self, char_pos: int) -> int:
        return self.label.get_char_pos(char_pos)[0] + self.label.width // 2 - self.x

    def set_text(self, text: str) -> None:
        self.text = text
        self.label.text_color = self.text_color
        self.label.set_text(text)
        self.cursor_pos = len(text) - 1

    def set_hint(self, hint: str) -> None:
        self.hint = hint
        self.label.set_text(self.hint)
        self.label.text_color = self.hint_text_color

    def render(self) -> None:
        if Settings().get_settings()["high_quality_graphics"] and self.border_radius:
            render_rounded_rect(self.canvas, self.color, self.get_rect(), self.border_radius)
        else:
            pygame.draw.rect(self.canvas, self.color, self.get_rect(), border_radius=self.border_radius)

        if self.border_width:
            border_color = self.border_color
            if self.focused:
                border_color = brighten(self.border_color, 100)
            elif self.hovering:
                border_color = brighten(self.border_color, 50)

            if Settings().get_settings()["high_quality_graphics"] and self.border_radius:
                render_rounded_rect(
                    self.canvas, border_color, self.get_rect(), self.border_radius, width=self.border_width
                )
            else:
                pygame.draw.rect(
                    self.canvas, border_color, self.get_rect(), border_radius=self.border_radius,
                    width=self.border_width
                )

        if self.underline is not None:
            pygame.draw.line(
                self.canvas, self.underline, (self.x - self.width // 2 + 4, self.y + self.height // 2 - 4),
                (self.x + self.width // 2 - 4, self.y + self.height // 2 - 4)
            )

        if self.label is not None:
            self.label.render()

        if self.render_cursor and self.focused:
            end_x, end_y = self.label.get_char_pos(self.cursor_pos)
            text_height = self.label.get_text_height()
            end_x = end_x or 0
            end_y = end_y or 0

            pygame.draw.line(self.canvas, self.text_color, (end_x, end_y), (end_x, end_y + text_height), 2)

        # UI debugging
        if UIDebugger.is_enabled():
            pygame.draw.rect(self.canvas, UIDebugger.box_color, self.get_rect(), 1)
            pygame.draw.circle(self.canvas, UIDebugger.center_point_color, (self.x, self.y), 2)

    def create_allowed_charset(self) -> set[str]:
        letters = string.ascii_lowercase + "ćčđšž"
        numbers = string.digits
        s = set(letters + letters.upper() + numbers + string.printable[:-2])
        s.remove("\t")
        return s

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.label.update_canvas(self.canvas)

    def update_position(self, x: int = None, y: int = None) -> None:
        self.label.x += (self.x - (self.x if x is None else x))
        self.label.y += (self.y - (self.y if y is None else y))
        self.x = self.x if x is None else x
        self.y = self.y if y is None else y

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.label.resize(width=self.width - self.padding.left - self.padding.right,
                          height=self.height - self.padding.top - self.padding.bottom)

        self.label.x = self.x + self.padding.left - self.padding.right
        if self.label.width % 2:
            self.label.x -= 1

    def set_focus(self, b: bool) -> None:
        if b:
            self.focused = True
            if not self.text:
                self.label.set_text("")
        else:
            self.focused = False
            if not self.text:
                self.label.set_text(self.hint)
                self.label.text_color = self.hint_text_color

    def on_click(self) -> None:
        pass

    def on_release(self, event: MouseReleaseEvent) -> None:
        if self.is_hovering((event.x, event.y)):
            self.focused = True
            if self.text:
                self.cursor_pos = self.label.get_closest_character(event.x, event.y)
            else:
                self.label.set_text("")
        else:
            self.focused = False
            if not self.text:
                self.label.set_text(self.hint)
                self.label.text_color = self.hint_text_color

        self.on_focus_changed(self.focused)

    def bind_on_enter(self, on_enter: Callable) -> None:
        self.on_enter = on_enter

    def bind_on_exit(self, on_exit: Callable) -> None:
        self.on_exit = on_exit

    def bind_on_key(self, on_key: Callable) -> None:
        self.on_key = on_key

    def bind_on_focus_changed(self, on_focus_changed: Callable) -> None:
        self.on_focus_changed = on_focus_changed

    def is_hovering(self, mouse_pos) -> bool:
        return self.get_rect().collidepoint(*mouse_pos)

    def is_deleting_initiated(self) -> bool:
        return self.backspace_pressed_time and time.time() - self.backspace_pressed_time > self.initiate_deleting_time

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
