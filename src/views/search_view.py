from typing import Union, Callable

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, Event, \
    MouseMotionEvent, LanguageChangedEvent
from src.events.event_loop import EventLoop
from src.events.mouse_buttons import MouseButtons
from src.models.calendar_model import CalendarModel, CalendarEvent
from src.ui.alignment import HorizontalAlignment
from src.ui.colors import Colors
from src.ui.image import Image
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.text_field import TextField
from src.ui.ui_object import UIObject
from src.utils.assets import Assets
from src.main.language_manager import LanguageManager
from src.views.view import View


class SearchEvent(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), event: CalendarEvent) -> None:
        super().__init__(canvas, pos)
        self.canvas = canvas
        self.x, self.y = pos
        self.width, self.height = size
        self.event = event

        self.ui_canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.hovering = False
        self.pressed = False

        self.on_release = None

        self.description_label = Label(
            self.ui_canvas,
            (self.width // 2 - 35, self.height // 2),
            (self.width - 90, self.height),
            text=self.event.description,
            text_color=(210, 210, 210),
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT,
            wrap_text=False
        )

        self.datetime_label = Label(
            self.ui_canvas,
            (self.width - 40, self.height // 2),
            (80, self.height),
            text=str(self.event.date).replace("-", "/") + "\n" + str(self.event.time)[:-3],
            text_color=(210, 210, 210),
            font=Assets().font14
        )

    def register_event(self, event: Event) -> bool:
        if (
                isinstance(event, MouseClickEvent) and
                self.get_rect().collidepoint((event.x, event.y)) and
                event.button is MouseButtons.LEFT_BUTTON
        ):
            self.pressed = True
            return True
        elif isinstance(event, MouseReleaseEvent) and self.pressed and event.button is MouseButtons.LEFT_BUTTON:
            self.on_release()
            self.pressed = False
            return True
        elif isinstance(event, MouseMotionEvent):
            if self.get_rect().collidepoint((event.x, event.y)):
                self.hovering = True
            else:
                self.hovering = False
            return True

    def render(self) -> None:
        self.ui_canvas.fill((0, 0, 0, 0))

        pygame.draw.rect(self.ui_canvas, (50, 50, 50) if self.hovering else Colors.BACKGROUND_GREY22, (0, 0, self.width, self.height), border_radius=4)
        pygame.draw.rect(self.ui_canvas, self.event.color, (0, 0, self.width, self.height), border_radius=4, width=1)

        self.description_label.render()
        self.datetime_label.render()

        self.canvas.blit(self.ui_canvas, (self.x - self.width // 2, self.y - self.height // 2))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.ui_canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.description_label.resize(width - 90, height)
        self.description_label.x = self.width // 2 - 35
        self.description_label.update_canvas(self.ui_canvas)

        self.datetime_label.resize(80, height)
        self.datetime_label.x = self.width - 40
        self.datetime_label.update_canvas(self.ui_canvas)

    def update_position(self, x: int = None, y: int = None) -> None:
        self.x = x or self.x
        self.y = y or self.y

    def bind_on_release(self, on_release: Callable[[int], None]) -> None:
        self.on_release = lambda event=self.event: on_release(event)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)


class SearchView(View):

    def __init__(self, display: pygame.Surface, model: CalendarModel, event_loop: EventLoop, width: int, height: int,
                 x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.model = model
        self.event_loop = event_loop
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.rendering = False

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.on_click = None
        self.on_release = None
        self.on_mouse_motion = None
        self.on_scroll = None

        self.on_search_event_release = None

        self.event_list_start_pos = (self.width // 2, 100)

        self.title_label = Label(
            self.canvas,
            (self.width // 2, self.height // 2),
            (200, 50),
            text=self.language_manager.get_string("event_appear_message"),
            text_color=(100, 100, 100),
            font=Assets().font18
        )

        self.search_bar = TextField(
            self.canvas,
            (self.width // 2, 35),
            (self.width - 20, 36),
            hint=self.language_manager.get_string("search_events") + "...",
            label=Label(text_color=(160, 160, 160), font=Assets().font18,
                        horizontal_text_alignment=HorizontalAlignment.LEFT),
            color=Colors.BACKGROUND_GREY22,
            border_color=Colors.GREY70,
            border_radius=6,
            max_length=100,
            hint_text_color=(100, 100, 100),
            oneline=True,
            padding=Padding(left=30, right=15)
        )

        self.search_bar_icon = Image(
            self.canvas,
            (self.width // 2 - self.search_bar.width // 2 + 20, 35),
            Assets().search_icon_large,
            size=(20, 20)
        )

        # self.search_bar_button = Button(
        #     self.canvas,
        #     (self.width // 2 - self.search_bar.width // 2 + 20, 35),
        #     (20, 20),
        #     color=Colors.BACKGROUND_GREY22,
        #     border_width=0,
        #     image=Assets().search_icon_large,
        #     hover_image=Assets().search_icon_large_hover,
        #     apply_hover_effects=False
        # )

        self.events = []

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, LanguageChangedEvent):
            self.update_language()

        event = self.get_event(event)

        if self.title_label.register_event(event):
            registered_events = True
        if self.search_bar.register_event(event):
            registered_events = True

        for search_event in self.events:
            if search_event.get_rect().top < self.height and search_event.register_event(event):
                registered_events = True

        if isinstance(event, MouseClickEvent) and self.on_click and event.button is MouseButtons.LEFT_BUTTON:
            self.on_click(event)
        elif isinstance(event, MouseReleaseEvent) and self.on_release and event.button is MouseButtons.LEFT_BUTTON:
            self.on_release(event)
        elif isinstance(event, MouseMotionEvent) and self.on_mouse_motion(event):
            return True
        elif isinstance(event, (MouseWheelUpEvent, MouseWheelDownEvent)):
            self.on_scroll(event)

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        for event in self.events:
            if event.get_rect().top < self.height:
                event.render()

        self.render_shadow()

        if not self.events:
            self.title_label.render()
        self.search_bar.render()
        self.search_bar_icon.render()

        pygame.draw.line(self.canvas, Colors.GREY70, (self.width - 1, 0), (self.width - 1, self.height))

        self.display.blit(self.canvas, (self.x, self.y))

    def render_shadow(self) -> None:
        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, [0, 0, self.width, 60])
        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, (0, self.height - 10, self.width, 10))
        c = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
        for i in range(22):
            y = self.event_list_start_pos[1] - 40 + i
            pygame.draw.line(c, (30, 30, 30, 255 - i * 12), (0, y), (self.width, y))
        for i in range(22):
            y = self.height - 10 - i
            pygame.draw.line(c, (30, 30, 30, 255 - i * 12), (0, y), (self.width, y))
        self.canvas.blit(c, (0, 0))

    def create_search_events(self, events: [CalendarEvent]) -> None:
        self.events = []

        for i, event in enumerate(events):
            self.events.append(
                SearchEvent(
                    self.canvas,
                    (self.width // 2, self.event_list_start_pos[1] + (i * 60)),
                    (self.width - 20, 50),
                    event
                )
            )

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.title_label.update_canvas(self.canvas)
        self.search_bar.update_canvas(self.canvas)
        self.search_bar_icon.update_canvas(self.canvas)

        for event in self.events:
            if event.get_rect().top < self.height:
                event.update_canvas(self.canvas)
                event.resize(self.width - 20)
                event.x = self.width // 2

        self.title_label.x = self.width // 2
        self.search_bar.x = self.width // 2
        self.search_bar.resize(width=self.width - 20)
        self.search_bar_icon.x = self.width // 2 - self.search_bar.width // 2 + 20

    def update_language(self) -> None:
        self.title_label.set_text(self.language_manager.get_string("search_events"))

    def bind_search_event_methods(self) -> None:
        for event in self.events:
            event.bind_on_release(self.on_search_event_release)

    def bind_on_search_event_release(self, on_search_event_release: Callable[[CalendarEvent], None]) -> None:
        self.on_search_event_release = on_search_event_release

    def bind_on_click(self, on_click: Callable[[MouseClickEvent], None]) -> None:
        self.on_click = on_click

    def bind_on_release(self, on_release: Callable[[MouseReleaseEvent], None]) -> None:
        self.on_release = on_release

    def bind_on_mouse_motion(self, on_mouse_motion: Callable[[MouseMotionEvent], bool]) -> None:
        self.on_mouse_motion = on_mouse_motion

    def bind_on_scroll(self, on_scroll: Callable[[Union[MouseWheelDownEvent, MouseWheelUpEvent]], bool]) -> None:
        self.on_scroll = on_scroll

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return 150, 170

