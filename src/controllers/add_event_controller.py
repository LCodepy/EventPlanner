import time
from typing import Callable

from src.events.event import CloseViewEvent, AddCalendarEventEvent, EditCalendarEventEvent
from src.events.event_loop import EventLoop
from src.ui.colors import Colors, Color
from src.utils.assets import Assets
from src.utils.ui_utils import adjust_dropdown_font_size
from src.views.add_event_view import AddEventView


class AddEventController:

    def __init__(self, view: AddEventView, event_loop: EventLoop) -> None:
        self.view = view
        self.event_loop = event_loop

        self.view.close_button.bind_on_click(self.on_close)
        self.view.bind_on_add_button_click(self.add_event)
        self.view.bind_color_buttons(self.on_color_button_click)

        self.view.dropdown.bind_on_release(lambda: adjust_dropdown_font_size(self.view.dropdown))
        self.view.dropdown.bind_on_select(self.on_dropdown_select)

    def on_color_button_click(self, color: Color) -> Callable:
        def apply_color() -> None:
            for btn in self.view.color_buttons:
                if btn.color == color:
                    btn.border_color = Colors.WHITE
                    btn.border_width = 1
                else:
                    btn.border_width = 0
        return apply_color

    def on_close(self) -> None:
        self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.view))

    def add_event(self) -> None:
        color = Colors.EVENT_BLUE204
        for btn in self.view.color_buttons:
            if btn.border_width != 0:
                color = btn.color

        try:
            event_time = self.view.get_time()
        except ValueError:
            self.view.show_error(self.view.invalid_time_error)
            return

        if self.view.editing_state:
            self.event_loop.enqueue_event(
                EditCalendarEventEvent(
                    time.time(), self.view.event_to_edit, event_time, self.view.description_text_field.text,
                    color, self.view.get_event_recurring()
                )
            )
        else:
            self.event_loop.enqueue_event(
                AddCalendarEventEvent(
                    time.time(), event_time, self.view.description_text_field.text, color,
                    self.view.get_event_recurring()
                )
            )

    def on_dropdown_select(self) -> None:
        self.view.dropdown.label.font = Assets().font20
        adjust_dropdown_font_size(self.view.dropdown)

