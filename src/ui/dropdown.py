import time
from typing import Callable, Union, Optional

import pygame

from src.events.event import Event, MouseMotionEvent, MouseReleaseEvent, MouseClickEvent, MouseFocusChangedEvent, \
    WindowMinimizedEvent, WindowUnminimizedEvent, MouseWheelUpEvent, MouseWheelDownEvent
from src.events.mouse_buttons import MouseButtons
from src.main.settings import Settings
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.colors import Color, Colors, brighten
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.rendering import render_rounded_rect
from src.utils.ui_debugger import UIDebugger


class DropDown(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), options: list[str],
                 color: Color = Colors.WHITE, border_color: Color = Colors.BLACK, text_color: Color = Colors.WHITE,
                 border_radius: int = 0, border_width: int = 1, hover_color: Color = None, click_color: Color = None,
                 selected_option: int = 0, font: pygame.font.Font = None, underline: bool = False,
                 horizontal_text_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
                 button_height: int = None, button_border_radius: int = None, scroll_value: int = 10,
                 max_height: int = None, padding: Padding = None) -> None:
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
        self.underline = underline
        self.horizontal_text_alignment = horizontal_text_alignment
        self.button_height = button_height or (self.height - 6)
        self.button_border_radius = button_border_radius
        self.scroll_value = scroll_value
        self.max_height = max_height
        self.padding = padding or Padding()

        self.scroll = 0
        self.scroller = pygame.Rect(self.width - 6, 1, 5, self.max_height // 4)

        self.box_surface = pygame.Surface((self.width, self.get_box_height()), pygame.SRCALPHA)

        self.hovering = False
        self.pressed = False
        self.opened = False
        self.is_scrolling = False
        self.scroller_pressed = False

        self.on_select = None
        self.on_release_bind = None
        self.on_click_bind = None

        self.label = Label(
            self.canvas,
            (self.x, self.y),
            (self.width, self.height),
            text=self.options[self.selected_option],
            text_color=self.text_color,
            font=self.font,
            horizontal_text_alignment=horizontal_text_alignment
        )
        self.label.x += self.padding.left - self.padding.right
        self.label.y += self.padding.top - self.padding.bottom

        self.buttons: list[Button] = []

    def register_event(self, event: Event) -> bool:
        self.is_scrolling = False

        registered_events = False

        ev = event
        if not self.event_in_box(event):
            ev = MouseFocusChangedEvent(time.time(), False)

        for btn in self.buttons:
            if btn.register_event(self.get_button_event(ev)):
                registered_events = True

        if isinstance(event, MouseMotionEvent):
            currently_hovering = self.is_hovering((event.x, event.y))
            if currently_hovering != self.hovering:
                if self.hovering:
                    self.on_exit()
                else:
                    self.on_enter()
                self.hovering = currently_hovering
            self.on_mouse_motion(event)
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
                (self.is_hovering((event.x, event.y)) or self.is_hovering_box((event.x, event.y))) and
                event.button is MouseButtons.LEFT_BUTTON
        ):
            self.pressed = True
            self.on_click(event)
            return True
        elif isinstance(event, MouseReleaseEvent) and event.button is MouseButtons.LEFT_BUTTON and self.scroller_pressed:
            self.scroller_pressed = False
        elif (
                isinstance(event, MouseReleaseEvent) and
                (self.is_hovering((event.x, event.y)) or self.is_hovering_box((event.x, event.y))) and
                event.button is MouseButtons.LEFT_BUTTON and
                self.pressed
        ):
            self.pressed = False
            self.on_release(event)
            return True
        elif isinstance(event, (MouseWheelUpEvent, MouseWheelDownEvent)) and self.is_hovering_box((event.x, event.y)):
            self.on_scroll(event)
            return True
        elif (
                isinstance(event, MouseClickEvent) and
                not self.is_hovering((event.x, event.y)) and not self.is_hovering_box((event.x, event.y)) and
                (event.button is MouseButtons.LEFT_BUTTON or event.button is MouseButtons.RIGHT_BUTTON)
        ):
            self.opened = False
            self.buttons = []
            return True

        return registered_events

    def render(self) -> None:
        if self.underline:
            pygame.draw.line(
                self.canvas, self.label.text_color, (self.x - self.width // 2, self.y + self.height // 2 - 2),
                (self.x + self.width // 2 - 1, self.y + self.height // 2 - 2)
            )
        elif Settings().get_settings()["high_quality_graphics"]:
            render_rounded_rect(self.canvas, self.color, self.get_rect(), self.border_radius, width=0)
            if self.border_width:
                render_rounded_rect(
                    self.canvas, self.border_color, self.get_rect(), self.border_radius, width=self.border_width
                )
        else:
            pygame.draw.rect(self.canvas, self.color, self.get_rect(), border_radius=self.border_radius)
            if self.border_width:
                pygame.draw.rect(
                    self.canvas, self.border_color, self.get_rect(), width=self.border_width,
                    border_radius=self.border_radius
                )

        self.label.render()

        if self.opened:
            if Settings().get_settings()["high_quality_graphics"]:
                render_rounded_rect(
                    self.canvas,
                    self.color,
                    pygame.Rect(
                        self.get_rect().x, self.y + self.height // 2, self.width, self.get_box_height()
                    ),
                    self.border_radius,
                    width=0
                )
            else:
                pygame.draw.rect(
                    self.canvas, self.color, [self.get_rect().x, self.y + self.height // 2, self.width,
                                              self.get_box_height()],
                    border_radius=self.border_radius
                )

        self.box_surface.fill((0, 0, 0, 0))

        for btn in self.buttons:
            btn.render()

        if self.max_height and self.opened:
            pygame.draw.rect(self.box_surface, (10, 10, 10), [self.width - 6, 1, 5, self.get_box_height() - 2])
            pygame.draw.rect(self.box_surface, (50, 50, 50), self.scroller, border_radius=2)

        if self.opened and self.border_width:
            if Settings().get_settings()["high_quality_graphics"]:
                render_rounded_rect(
                    self.box_surface,
                    self.border_color,
                    pygame.Rect(0, 0, self.width, self.get_box_height()),
                    self.border_radius,
                    width=self.border_width
                )
            else:
                pygame.draw.rect(
                    self.box_surface, self.border_color, [0, 0, self.width, self.get_box_height()],
                    border_radius=self.border_radius, width=self.border_width
                )

        self.canvas.blit(self.box_surface, (self.get_box_rect().x, self.get_box_rect().y))

        # UI debugging
        if UIDebugger.is_enabled():
            pygame.draw.circle(self.canvas, UIDebugger.center_point_color, (self.x, self.y), 2)

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.label.update_canvas(self.canvas)

    def update_position(self, x: int = None, y: int = None) -> None:
        self.label.x -= (self.x - (self.x if x is None else x))
        self.label.y -= (self.y - (self.y if y is None else y))
        self.x = self.x if x is None else x
        self.y = self.y if y is None else y

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
                    self.box_surface,
                    (self.width // 2 if not self.max_height else self.width // 2 - 2,
                     self.height // 2 + 3 + i * self.button_height + (self.height - self.button_height) // 2),
                    (self.button_width, self.button_height),
                    label=Label(text=self.options[j], text_color=self.text_color, font=self.font,
                                horizontal_text_alignment=self.horizontal_text_alignment),
                    color=self.color,
                    border_width=0,
                    border_radius=self.button_border_radius or self.border_radius,
                    padding=self.padding
                )
            )
            self.buttons[i].bind_on_click(lambda idx=j: self.on_button_click(idx))
            i += 1

    def get_selected_option(self) -> str:
        return self.options[self.selected_option]

    def set_option(self, idx: int) -> None:
        self.selected_option = idx
        self.label.set_text(self.options[idx])

    def set_max_height(self, height: Optional[int]) -> None:
        self.max_height = height
        self.box_surface = pygame.Surface((self.width, self.get_box_height()), pygame.SRCALPHA)
        for btn in self.buttons:
            btn.update_canvas(self.box_surface)

    def set_scroll(self) -> None:
        self.scroll = -self.scroller.y * (self.get_box_height(False) - self.max_height) / (
                    self.max_height - self.scroller.h)
        for i, btn in enumerate(self.buttons):
            btn.update_position(
                y=self.height // 2 + 3 + i * self.button_height + (self.height - self.button_height) // 2 + self.scroll
            )

    def on_button_click(self, idx: int) -> None:
        self.selected_option = idx
        self.label.set_text(self.options[idx])
        self.opened = False
        self.buttons = []

        if self.on_select:
            self.on_select()

    def on_mouse_motion(self, event: MouseMotionEvent) -> None:
        event = self.get_button_event(event)

        if self.scroller_pressed and self.pressed:
            self.scroller.y = max(0, min(self.max_height - self.scroller.h, event.y - self.scroller.h // 2))
            self.set_scroll()

    def on_click(self, event: MouseClickEvent) -> None:
        event = self.get_button_event(event)

        if not self.scroller.collidepoint((event.x, event.y)) and event.x > self.width - 7:
            self.scroller_pressed = True
            self.scroller.y = max(0, min(self.max_height - self.scroller.h, event.y - self.scroller.h // 2))
            self.set_scroll()
        elif self.scroller.collidepoint((event.x, event.y)):
            self.scroller_pressed = True

        if self.on_click_bind:
            self.on_click_bind()

    def on_release(self, event: MouseReleaseEvent) -> None:
        if self.is_hovering_box((event.x, event.y)):
            return

        if self.opened:
            self.opened = False
            self.buttons = []
            return

        self.opened = True
        self.create_buttons()

        if self.on_release_bind:
            self.on_release_bind()

    def on_enter(self) -> None:
        self.label.text_color = self.hover_color

    def on_exit(self) -> None:
        self.label.text_color = self.text_color

    def on_scroll(self, event: Union[MouseWheelUpEvent, MouseWheelDownEvent]) -> None:
        self.is_scrolling = True

        scroll_value = self.scroll_value * event.scroll
        min_y = self.buttons[0].get_rect().top
        max_y = self.buttons[-1].get_rect().bottom

        if (
                (isinstance(event, MouseWheelUpEvent) and min_y < 3) or
                (isinstance(event, MouseWheelDownEvent) and max_y > self.get_box_height() - 3)
        ):
            if max_y + scroll_value <= self.get_box_height() - 3:
                scroll_value = self.get_box_height() - 3 - max_y
            elif min_y + scroll_value >= 3:
                scroll_value = 3 - min_y

            self.scroll += scroll_value
            self.scroller.y = -self.scroll * (self.max_height - self.scroller.h) / (self.get_box_height(False) - self.max_height)
            for btn in self.buttons:
                btn.update_position(y=btn.y + scroll_value)

    def bind_on_click(self, on_click: Callable) -> None:
        self.on_click_bind = on_click

    def bind_on_release(self, on_release: Callable) -> None:
        self.on_release_bind = on_release

    def bind_on_select(self, on_select: Callable) -> None:
        self.on_select = on_select

    def is_hovering(self, mouse_pos: (int, int)) -> bool:
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

    def is_hovering_box(self, mouse_pos: (int, int)) -> bool:
        if not self.opened:
            return False

        return self.get_box_rect().collidepoint(mouse_pos)

    def event_in_box(self, event: Event) -> bool:
        if not isinstance(
                event, (MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, MouseMotionEvent)
               ):
            return True
        elif self.get_box_rect().top < event.y < self.get_box_rect().bottom:
            return True
        return False

    def get_button_event(self, event: Event) -> Event:
        if isinstance(event, (MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent)):
            return event.__class__(event.exec_time, event.x - self.get_box_rect().x, event.y - self.get_box_rect().y,
                                   *list(event.__dict__.values())[3:])
        elif isinstance(event, MouseMotionEvent):
            return MouseMotionEvent(
                event.exec_time, event.start_x - self.get_box_rect().x, event.start_y - self.get_box_rect().y,
                                 event.x - self.get_box_rect().x, event.y - self.get_box_rect().y
            )
        return event

    def get_box_height(self, max_height: bool = True) -> int:
        if max_height:
            return self.max_height or self.button_height * (len(self.options) - 1) + 6
        return self.button_height * (len(self.options) - 1) + 6

    def get_box_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y + self.height // 2, self.width, self.get_box_height())

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    @property
    def button_width(self) -> None:
        if self.max_height:
            return self.width - 10
        return self.width - 6
