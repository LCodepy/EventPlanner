from typing import Callable

import pygame

from src.events.event import Event, MouseMotionEvent, MouseReleaseEvent, MouseClickEvent, MouseFocusChangedEvent, \
    WindowMinimizedEvent, WindowUnminimizedEvent
from src.events.mouse_buttons import MouseButtons
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.colors import Color, Colors, brighten
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.ui_debugger import UIDebugger


class DropDown(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), options: list[str],
                 color: Color = Colors.WHITE, border_color: Color = Colors.BLACK, text_color: Color = Colors.WHITE,
                 border_radius: int = 0,  border_width: int = 1,  hover_color: Color = None, click_color: Color = None,
                 selected_option: int = 0, font: pygame.font.Font = None,
                 horizontal_text_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
                 padding: Padding = None) -> None:
        super().__init__(canvas, pos, padding)
        self.canvas = canvas
        self.x, self.y = pos
        self.width, self.height = size

        self.options = options
        self.color = color
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.hover_color = hover_color or brighten(self.text_color, 20)
        self.click_color = click_color or brighten(self.text_color, 30)
        self.selected_option = selected_option
        self.font = font or pygame.font.SysFont("arial", 12)
        self.padding = padding or Padding()

        self.hovering = False
        self.pressed = False
        self.opened = False

        self.label = Label(
            self.canvas,
            (self.x, self.y),
            (self.width, self.height),
            text=self.options[self.selected_option],
            text_color=self.text_color,
            font=self.font,
            horizontal_text_alignment=horizontal_text_alignment
        )

        self.buttons: list[Button] = []

    def register_event(self, event: Event) -> bool:
        registered_events = False

        for btn in self.buttons:
            if btn.register_event(event):
                registered_events = True

        if registered_events:
            return True

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
        elif (
            isinstance(event, MouseClickEvent) and
            not self.is_hovering((event.x, event.y))
        ):
            self.opened = False
            self.buttons = []
            return True

    def render(self) -> None:
        pygame.draw.line(self.canvas, self.label.text_color, (self.x - self.width // 2, self.y + self.height // 2),
                         (self.x + self.width // 2 - 1, self.y + self.height // 2))

        self.label.render()

        if self.opened:
            pygame.draw.rect(self.canvas, self.color,
                             [self.get_rect().x, self.y + self.height // 2, self.width, (self.height - 4) * 3],
                             border_radius=self.border_radius)
            if self.border_width:
                pygame.draw.rect(self.canvas, self.border_color,
                                 [self.get_rect().x, self.y + self.height // 2, self.width, (self.height - 4) * 3],
                                 border_radius=self.border_radius, width=self.border_width)

        for btn in self.buttons:
            btn.render()

        # UI debugging
        if UIDebugger.is_enabled():
            pygame.draw.circle(self.canvas, UIDebugger.center_point_color, (self.x, self.y), 2)

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.label.update_canvas(self.canvas)

    def update_position(self, x: int = None, y: int = None) -> None:
        self.label.x -= (self.x - (x or self.x))
        self.label.y -= (self.y - (y or self.y))
        self.x = x or self.x
        self.y = y or self.y

    def update_options(self, options: list[str]) -> None:
        self.options = options
        self.label.set_text(self.options[self.selected_option])
        self.create_buttons()

    def create_buttons(self) -> None:
        self.buttons = []
        i = 0
        for j in range(len(self.options)):
            if j == self.selected_option:
                continue
            self.buttons.append(
                Button(
                    self.canvas,
                    (self.x, self.y + 6 + (i + 1) * (self.height - 6)),
                    (self.width - 6, self.height - 6),
                    label=Label(text=self.options[j], text_color=self.text_color, font=self.font),
                    color=self.color,
                    border_width=0,
                    border_radius=0
                )
            )
            self.buttons[i].bind_on_click(lambda idx=j: self.on_button_click(idx))
            i += 1

    def get_selected_option(self) -> str:
        return self.options[self.selected_option]

    def set_option(self, idx: int) -> None:
        self.selected_option = idx
        self.label.set_text(self.options[idx])

    def on_button_click(self, idx: int) -> None:
        self.selected_option = idx
        self.label.set_text(self.options[idx])
        self.opened = False
        self.buttons = []

    def on_click(self) -> None:
        pass

    def on_release(self) -> None:
        if self.opened:
            self.opened = False
            self.buttons = []
            return

        self.opened = True
        self.create_buttons()

    def on_enter(self) -> None:
        self.label.text_color = self.hover_color

    def on_exit(self) -> None:
        self.label.text_color = self.text_color

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



