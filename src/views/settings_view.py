from typing import Union, Callable

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, Event, MouseWheelUpEvent, MouseWheelDownEvent, \
    LanguageChangedEvent, MouseMotionEvent
from src.events.mouse_buttons import MouseButtons
from src.main.config import Config
from src.main.language_manager import LanguageManager
from src.main.settings import Settings
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.check_box import CheckBox
from src.ui.colors import Colors
from src.ui.dropdown import DropDown
from src.ui.label import Label
from src.ui.padding import Padding
from src.utils.assets import Assets
from src.views.view import View


class SettingsView(View):

    def __init__(self, display: pygame.Surface, width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.on_click = None
        self.on_release = None
        self.on_mouse_motion = None
        self.on_scroll = None

        self.title_label = Label(
            self.canvas,
            (self.width // 2, 50),
            (self.width, 50),
            text="Settings",
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font32
        )

        self.general_label = Label(
            self.canvas,
            (110, 140),
            (200, 40),
            text="General",
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font24,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.language_label = Label(
            self.canvas,
            (120, 200),
            (200, 40),
            text="Language",
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.language_label2 = Label(
            self.canvas,
            (170, 225),
            (300, 20),
            text="Select display language",
            text_color=Colors.TEXT_GREY,
            font=Assets().font14,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.language_dropdown = DropDown(
            self.canvas,
            (120, 260),
            (200, 30),
            list(map(lambda l: l.upper(), self.language_manager.languages)),
            color=Colors.BACKGROUND_GREY22,
            border_color=Colors.GREY70,
            text_color=Colors.TEXT_LIGHT_GREY,
            border_radius=4,
            border_width=1,
            font=Assets().font16,
            horizontal_text_alignment=HorizontalAlignment.LEFT,
            padding=Padding(left=10),
            selected_option=self.language_manager.languages.index(self.language_manager.get_language_name())
        )

        self.catholic_events_label = Label(
            self.canvas,
            (170, 320),
            (300, 40),
            text="Catholic Events",
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.show_catholic_events_label = Label(
            self.canvas,
            (200, 350),
            (300, 20),
            text="Show all catholic events",
            text_color=Colors.TEXT_GREY,
            font=Assets().font14,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.catholic_events_checkbox = CheckBox(
            self.canvas,
            (30, 350),
            20,
            color=Colors.BACKGROUND_GREY22,
            border_color=Colors.GREY70,
            border_radius=4,
            border_width=1,
            checked=Settings().get_settings()["show_catholic_events"]
        )

        self.fill_events_label = Label(
            self.canvas,
            (170, 410),
            (300, 40),
            text="Filled Events",
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.fill_events_label2 = Label(
            self.canvas,
            (200, 440),
            (300, 20),
            text="Make events more colorful",
            text_color=Colors.TEXT_GREY,
            font=Assets().font14,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.fill_events_checkbox = CheckBox(
            self.canvas,
            (30, 440),
            20,
            color=Colors.BACKGROUND_GREY22,
            border_color=Colors.GREY70,
            border_radius=4,
            border_width=1,
            checked=Settings().get_settings()["render_filled_events"]
        )

        self.graphics_label = Label(
            self.canvas,
            (170, 500),
            (300, 40),
            text="High Quality Graphics",
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.graphics_label2 = Label(
            self.canvas,
            (200, 530),
            (300, 20),
            text="Enable high-quality graphics",
            text_color=Colors.TEXT_GREY,
            font=Assets().font14,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.graphics_checkbox = CheckBox(
            self.canvas,
            (30, 530),
            20,
            color=Colors.BACKGROUND_GREY22,
            border_color=Colors.GREY70,
            border_radius=4,
            border_width=1,
            checked=Settings().get_settings()["high_quality_graphics"]
        )

        self.account_label = Label(
            self.canvas,
            (110, 600),
            (200, 40),
            text="Account",
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font24,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.auto_sync_label = Label(
            self.canvas,
            (120, 660),
            (200, 40),
            text="Auto Sync",
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.auto_sync_label2 = Label(
            self.canvas,
            (200, 690),
            (300, 40),
            text="Enable auto syncing calendars",
            text_color=Colors.TEXT_GREY,
            font=Assets().font14,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.auto_sync_checkbox = CheckBox(
            self.canvas,
            (30, 690),
            20,
            color=Colors.BACKGROUND_GREY22,
            border_color=Colors.GREY70,
            border_radius=4,
            border_width=1,
            checked=Settings().get_settings()["autosync"]
        )

        self.sync_button = Button(
            self.canvas,
            (140, 760),
            (240, 36),
            label=Label(text="Sync Calendars", text_color=Colors.TEXT_LIGHT_GREY, font=Assets().font18),
            color=Colors.BACKGROUND_GREY22,
            border_radius=4,
            border_width=0
        )

        self.sign_out_button = Button(
            self.canvas,
            (140, 820),
            (240, 36),
            label=Label(text="Sign Out Of All Accounts", text_color=Colors.TEXT_LIGHT_GREY, font=Assets().font18),
            color=Colors.BACKGROUND_GREY22,
            border_radius=4,
            border_width=0
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, LanguageChangedEvent):
            self.update_language()

        event = self.get_event(event)

        for obj in self.get_ui_elements():
            if obj.register_event(event):
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

        for obj in self.get_ui_elements():
            if obj != self.language_dropdown:
                obj.render()

        self.language_dropdown.render()

        pygame.draw.line(
            self.canvas, Colors.TEXT_DARK_GREY, (10, self.general_label.y + 18),
            (self.width - 10, self.general_label.y + 18)
        )
        pygame.draw.line(
            self.canvas, Colors.TEXT_DARK_GREY, (10, self.account_label.y + 18),
            (self.width - 10, self.account_label.y + 18)
        )

        pygame.draw.line(self.canvas, Colors.GREY70, (self.width - 1, 0), (self.width - 1, self.height))

        self.display.blit(self.canvas, (self.x, self.y))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height
        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

        self.title_label.x = self.width // 2

    def update_language(self) -> None:
        pass

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
        return Config.side_view_min_size
