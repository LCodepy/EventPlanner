import datetime
import time
from typing import Union, Callable

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, Event, \
    MouseMotionEvent, AddCalendarEventEvent, DeleteCalendarEventEvent, OpenEditCalendarEventEvent, \
    EditCalendarEventEvent, LanguageChangedEvent, TimerEvent
from src.events.event_loop import EventLoop
from src.events.mouse_buttons import MouseButtons
from src.models.calendar_model import CalendarModel, CalendarEvent
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.animations import ChangeValuesAnimation
from src.utils.assets import Assets
from src.main.language_manager import LanguageManager
from src.views.view import View


class EventListEvent(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), event: CalendarEvent,
                 event_loop: EventLoop, padding: Padding = None) -> None:
        super().__init__(canvas, pos, padding)

        self.canvas = canvas
        self.x, self.y = pos
        self.width, self.height = size
        self.event = event
        self.event_loop = event_loop
        self.padding = padding

        self.editable = not self.event.is_default

        self.start_pos = (self.x, self.y)
        self.pressed = False
        self.pressed_right = False
        self.click_pos = None

        self.on_delete_callback = None
        self.on_open_options = None
        self.open_edit_calendar_event = None

        self.highlight_animation = ChangeValuesAnimation(
            "HighlightAnimation" + str(self.event.id), self.event_loop, 0.3
        )
        self.highlight_animation.bind_on_stop(lambda: self.highlight(1))

        self.description_label = Label(
            self.canvas,
            (self.x - 10, self.y),
            (self.width - 50, self.height),
            text=self.event.description,
            text_color=(200, 200, 200),
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT,
            wrap_text=True
        )
        self.resize_to_label_size()

        self.delete_task_button = Button(
            self.canvas,
            (self.x + self.width // 2 - Assets().delete_task_icon_large.get_width() // 2 - 5, self.y),
            (Assets().delete_task_icon_large.get_width(), Assets().delete_task_icon_large.get_height()),
            image=Assets().delete_task_icon_large,
            hover_image=Assets().delete_task_icon_large_hover,
            color=Colors.BACKGROUND_GREY30,
            hover_color=Colors.BACKGROUND_GREY30,
            click_color=Colors.BACKGROUND_GREY30,
            border_width=0
        )
        if self.editable:
            self.delete_task_button.bind_on_click(self.on_delete)

    def register_event(self, event: Event) -> bool:
        if self.highlight_animation.register_event(event):
            return True

        if self.editable and self.delete_task_button.register_event(event):
            return True

        if isinstance(event, DeleteCalendarEventEvent) and event.event == self.event:
            self.on_delete()
        elif isinstance(event, OpenEditCalendarEventEvent) and event.event == self.event:
            self.open_edit_calendar_event(self.event)

        if (
                isinstance(event, MouseClickEvent) and
                self.get_rect().collidepoint((event.x, event.y)) and
                event.button is MouseButtons.LEFT_BUTTON
        ):
            self.pressed = True
            return True
        elif (
                isinstance(event, MouseClickEvent) and
                self.get_rect().collidepoint((event.x, event.y)) and
                event.button is MouseButtons.RIGHT_BUTTON
        ):
            self.pressed_right = True
            self.click_pos = (event.x, event.y)
            return True
        elif isinstance(event, MouseReleaseEvent) and self.pressed and event.button is MouseButtons.LEFT_BUTTON:
            self.pressed = False
            return True
        elif isinstance(event, MouseReleaseEvent) and self.pressed_right and event.button is MouseButtons.RIGHT_BUTTON:
            self.on_open_options(self.event)
            self.pressed_right = False
            return True
        elif isinstance(event, MouseMotionEvent) and self.pressed:
            return True

    def render(self) -> None:
        pygame.draw.rect(self.canvas, self.event.color, self.get_rect(), 2, 6)
        if self.highlight_animation.active and self.highlight_animation.values:
            c2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(c2, (255, 255, 255), [0, 0, self.width, self.height], 2, 6)
            c2.set_alpha(int(self.highlight_animation.values[0]))
            self.canvas.blit(c2, (self.x - self.width // 2, self.y - self.height // 2))

        self.description_label.render()
        if self.editable:
            self.delete_task_button.render()

    def highlight(self, order: int = 0) -> None:
        if order == 0:
            self.highlight_animation.start([0], [255])
            self.highlight_animation.bind_on_stop(lambda: self.highlight(1))
        else:
            self.highlight_animation.start([255], [0])
            self.highlight_animation.bind_on_stop(lambda: None)

    def update_event(self, event: CalendarEvent) -> None:
        self.event = event
        self.description_label.set_text(event.description)

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.description_label.canvas = self.canvas
        self.delete_task_button.canvas = self.canvas

    def update_position(self, x: int = None, y: int = None, set_start_pos: bool = False) -> None:
        if x is not None:
            self.description_label.x = x - 10
            self.delete_task_button.x = x + self.width // 2 - Assets().delete_task_icon_large.get_width() // 2 - 5
            self.x = x
            if set_start_pos:
                self.start_pos = (x, self.start_pos[1])
        if y is not None:
            self.description_label.y = y
            self.delete_task_button.y = y
            self.y = y
            if set_start_pos:
                self.start_pos = (self.start_pos[0], y)

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.description_label.resize(width=max(self.width - 50, 20), height=self.height)
        self.delete_task_button.x = self.x + self.width // 2 - Assets().delete_task_icon_large.get_width() // 2 - 5
        self.resize_to_label_size()

    def resize_to_label_size(self) -> None:
        self.description_label = Label(
            self.canvas,
            (self.x - 10, self.y),
            (max(self.width - 50, 20), self.description_label.get_min_label_size()[1] + 18),
            text=self.event.description,
            text_color=(200, 200, 200),
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT,
            wrap_text=True
        )
        self.height = self.description_label.get_min_label_size()[1] + 18

    def on_delete(self) -> None:
        self.on_delete_callback(self.event)

    def bind_on_delete(self, on_delete: Callable) -> None:
        self.on_delete_callback = on_delete

    def bind_on_open_options(self, on_open_options) -> None:
        self.on_open_options = on_open_options

    def bind_open_edit_calendar_event(self, open_edit_calendar_event: Callable) -> None:
        self.open_edit_calendar_event = open_edit_calendar_event

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - (self.height / 2).__ceil__(), self.width, self.height)


class EventListView(View):

    def __init__(self, display: pygame.Surface, model: CalendarModel, event_loop: EventLoop, width: int, height: int,
                 x: int, y: int, date: datetime.date) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.model = model
        self.event_loop = event_loop
        self.width = width
        self.height = height
        self.date = date
        self.x = x
        self.y = y

        self.rendering = False

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.on_click = None
        self.on_release = None
        self.on_mouse_motion = None
        self.on_scroll = None
        self.on_resize = None

        self.add_event = None
        self.edit_event = None

        self.event_to_highlight = None

        self.event_list_x = self.width // 5
        self.events_pos = ((self.width - self.event_list_x) // 2 + self.event_list_x, 120)
        self.events_size = (self.width - self.event_list_x - 20, 40)
        self.scroll_offset = 0

        self.time_table: dict[datetime.time, list[EventListEvent]] = {}
        self.time_labels: list[Label] = []

        self.create_time_table()

        self.title_label = Label(
            self.canvas,
            (self.width // 2, 35),
            (150, 50),
            text=f"{self.date.day} / {self.date.month} / {self.date.year}",
            text_color=(160, 160, 160),
            font=Assets().font24
        )

        self.add_event_button = Button(
            self.canvas,
            (self.width // 2, self.height - 40),
            (120, 40),
            label=Label(
                text=self.language_manager.get_string("add_event"),
                text_color=(160, 160, 160),
                font=Assets().font18
            ),
            color=Colors.BLACK,
            hover_color=(50, 50, 50),
            click_color=(60, 60, 60),
            border_width=0,
            border_radius=3
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, AddCalendarEventEvent):
            self.add_event(event)
        elif isinstance(event, EditCalendarEventEvent):
            self.edit_event(event)
        elif isinstance(event, LanguageChangedEvent):
            self.update_language()

        if self.event_to_highlight:
            self.event_loop.enqueue_event(
                TimerEvent(time.time(), 0.2, lambda e=self.event_to_highlight: self.highlight_event(e))
            )
            self.event_to_highlight = None

        event = self.get_event(event)

        if self.title_label.register_event(event):
            registered_events = True
        if self.add_event_button.register_event(event):
            registered_events = True

        for evs in self.time_table.values():
            for ev in evs:
                if ev.register_event(event):
                    registered_events = True

        if isinstance(event, MouseClickEvent) and self.on_click and event.button is MouseButtons.LEFT_BUTTON:
            self.on_click(event)
        elif isinstance(event, MouseReleaseEvent) and self.on_release and event.button is MouseButtons.LEFT_BUTTON:
            self.on_release(event)
        elif isinstance(event, MouseMotionEvent) and self.on_mouse_motion(event):
            return True
        elif isinstance(event, (MouseWheelUpEvent, MouseWheelDownEvent)) and self.on_scroll(event):
            return True

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        pygame.draw.line(self.canvas, Colors.GREY70, (self.event_list_x, 60), (self.event_list_x, self.height - 80))
        pygame.draw.line(self.canvas, Colors.GREY70, (10, 100), (self.width - 10, 100))

        self.render_events()

        self.render_shadow()

        self.title_label.render()
        self.add_event_button.render()

        pygame.draw.line(self.canvas, Colors.GREY70, (self.width - 1, 0), (self.width - 1, self.height))

        self.display.blit(self.canvas, (self.x, self.y))

    def render_events(self) -> None:
        for t, events in self.time_table.items():
            for event in events:
                event.render()
            if events:
                for x in range(15, self.width - 15, 12):
                    pygame.draw.line(self.canvas, Colors.GREY70, (x, events[-1].get_rect().bottom + 20),
                                     (x + 6, events[-1].get_rect().bottom + 20))

        for label in self.time_labels:
            label.render()

    def render_shadow(self) -> None:
        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, [0, 0, self.width, 100])
        pygame.draw.rect(
            self.canvas, Colors.BACKGROUND_GREY30,
            [0, self.add_event_button.y - 40, self.width, self.height - self.add_event_button.y + 40]
        )
        c2 = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
        for i in range(22):
            y = self.add_event_button.y - 40 - i
            pygame.draw.line(c2, (30, 30, 30, 255 - i * 12), (0, y), (self.width, y))
        self.canvas.blit(c2, (0, 0))

    def create_time_table(self) -> None:
        self.time_table = {}
        for event in self.get_sorted_events():
            event_obj = EventListEvent(
                self.canvas, (self.events_pos[0], self.events_pos[1] + self.scroll_offset), self.events_size, event,
                self.event_loop
            )
            if event.time not in self.time_table:
                self.time_table[event.time] = []
            self.time_table[event.time].append(event_obj)

        self.time_labels = []
        current_y = self.events_pos[1] + self.scroll_offset
        for t, events in self.time_table.items():
            self.time_labels.append(Label(
                self.canvas, (30, current_y), (50, 40), text=t.isoformat()[:5],
                text_color=Colors.GREY140, font=Assets().font18
            ))

            for event in events:
                event.update_position(y=current_y + event.height // 2, set_start_pos=True)
                current_y += event.height + 10
            current_y += 30

    def highlight_event(self, event: CalendarEvent) -> None:
        for events in self.time_table.values():
            for ev in events:
                if ev.event == event:
                    ev.highlight()

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.title_label.update_canvas(self.canvas)
        self.add_event_button.update_canvas(self.canvas)
        for label in self.time_labels:
            label.update_canvas(self.canvas)

        for events in self.time_table.values():
            for event in events:
                event.update_canvas(self.canvas)

        self.add_event_button.update_position(y=self.height - 40)

        if not width:
            return

        self.events_pos = ((self.width - self.event_list_x) // 2 + self.event_list_x, 120)
        self.events_size = (self.width - self.event_list_x - 20, 40)
        self.title_label.x = self.width // 2
        self.add_event_button.update_position(x=self.width // 2)

        for events in self.time_table.values():
            for event in events:
                event.resize(width=self.events_size[0])
                event.update_position(x=self.events_pos[0])

        self.create_time_table()
        self.on_resize()

    def update_language(self) -> None:
        self.add_event_button.label.set_text(self.language_manager.get_string("add_event"))

    def get_sorted_events(self) -> list[CalendarEvent]:
        events = self.model.get_events_for_date(self.date)
        return sorted(events, key=lambda ev: ev.time)

    def bind_event_methods(self, delete_event: Callable, on_open_options: Callable, open_edit_calendar_event: Callable) -> None:
        for events in self.time_table.values():
            for event in events:
                event.bind_on_delete(delete_event)
                event.bind_on_open_options(on_open_options)
                event.bind_open_edit_calendar_event(open_edit_calendar_event)

    def bind_add_event(self, add_event: Callable) -> None:
        self.add_event = add_event

    def bind_edit_event(self, edit_event: Callable) -> None:
        self.edit_event = edit_event

    def bind_on_click(self, on_click: Callable[[MouseClickEvent], None]) -> None:
        self.on_click = on_click

    def bind_on_release(self, on_release: Callable[[MouseReleaseEvent], None]) -> None:
        self.on_release = on_release

    def bind_on_mouse_motion(self, on_mouse_motion: Callable[[MouseMotionEvent], bool]) -> None:
        self.on_mouse_motion = on_mouse_motion

    def bind_on_scroll(self, on_scroll: Callable[[Union[MouseWheelDownEvent, MouseWheelUpEvent]], bool]) -> None:
        self.on_scroll = on_scroll

    def bind_on_resize(self, on_resize: Callable) -> None:
        self.on_resize = on_resize

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return 150, 170

    @property
    def task_list_bottom(self) -> (int, int):
        return self.events_pos[0], self.add_event_button.y - 40

    @property
    def task_list_top(self) -> (int, int):
        return self.events_pos[0], self.events_pos[1]

