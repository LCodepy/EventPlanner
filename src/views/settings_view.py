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
from src.utils.ui_utils import adjust_labels_font_size
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
            (self.width - 10, 50),
            text=self.language_manager.get_string("settings"),
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font32
        )

        self.general_label = Label(
            self.canvas,
            (110, 140),
            (200, 40),
            text=self.language_manager.get_string("general"),
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font24,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.language_label = Label(
            self.canvas,
            (140, 200),
            (240, 40),
            text=self.language_manager.get_string("language"),
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.language_label2 = Label(
            self.canvas,
            (170, 225),
            (300, 20),
            text=self.language_manager.get_string("language_description"),
            text_color=Colors.TEXT_GREY,
            font=Assets().font14,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.language_dropdown = DropDown(
            self.canvas,
            (120, 260),
            (200, 30),
            self.language_manager.get_repr_languages(),
            color=Colors.BACKGROUND_GREY22,
            border_color=Colors.GREY70,
            text_color=Colors.TEXT_LIGHT_GREY,
            border_radius=4,
            border_width=1,
            font=Assets().font16,
            horizontal_text_alignment=HorizontalAlignment.LEFT,
            padding=Padding(left=10),
            selected_option=self.language_manager.languages.index(self.language_manager.get_language_name()),
            button_height=30,
            scroll_value=Config.scroll_value,
            max_height=200
        )

        self.catholic_events_label = Label(
            self.canvas,
            (140, 320),
            (240, 40),
            text=self.language_manager.get_string("catholic_events"),
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.show_catholic_events_label = Label(
            self.canvas,
            (200, 350),
            (300, 20),
            text=self.language_manager.get_string("catholic_events_description"),
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
            (140, 410),
            (240, 40),
            text=self.language_manager.get_string("filled_events"),
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.fill_events_label2 = Label(
            self.canvas,
            (200, 440),
            (300, 20),
            text=self.language_manager.get_string("filled_events_description"),
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
            (140, 500),
            (240, 40),
            text=self.language_manager.get_string("graphics"),
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.graphics_label2 = Label(
            self.canvas,
            (200, 530),
            (300, 20),
            text=self.language_manager.get_string("graphics_description"),
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
            text=self.language_manager.get_string("account"),
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font24,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.auto_sync_label = Label(
            self.canvas,
            (150, 660),
            (260, 40),
            text=self.language_manager.get_string("auto_sync"),
            text_color=Colors.TEXT_LIGHT_GREY,
            font=Assets().font18,
            horizontal_text_alignment=HorizontalAlignment.LEFT
        )

        self.auto_sync_label2 = Label(
            self.canvas,
            (225, 690),
            (350, 20),
            text=self.language_manager.get_string("auto_sync_description"),
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
            label=Label(text=self.language_manager.get_string("sync_calendars"),
                        text_color=Colors.TEXT_LIGHT_GREY, font=Assets().font18),
            color=Colors.BACKGROUND_GREY22,
            border_radius=4,
            border_width=0
        )

        self.sign_out_button = Button(
            self.canvas,
            (140, 820),
            (240, 36),
            label=Label(text=self.language_manager.get_string("sign_out_all"),
                        text_color=Colors.TEXT_LIGHT_GREY, font=Assets().font18),
            color=Colors.BACKGROUND_GREY22,
            border_radius=4,
            border_width=0
        )

        adjust_labels_font_size(self.get_ui_elements())

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
        elif isinstance(event, (MouseWheelUpEvent, MouseWheelDownEvent)) and not self.language_dropdown.is_scrolling and self.on_scroll(event):
            return True

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        for obj in self.get_ui_elements():
            if obj != self.language_dropdown and obj != self.title_label:
                obj.render()

        pygame.draw.line(
            self.canvas, Colors.TEXT_DARK_GREY, (10, self.general_label.y + 18),
            (self.width - 10, self.general_label.y + 18)
        )
        pygame.draw.line(
            self.canvas, Colors.TEXT_DARK_GREY, (10, self.account_label.y + 18),
            (self.width - 10, self.account_label.y + 18)
        )

        self.language_dropdown.render()

        self.render_shadow()

        self.title_label.render()

        pygame.draw.line(self.canvas, Colors.GREY70, (self.width - 1, 0), (self.width - 1, self.height))

        self.display.blit(self.canvas, (self.x, self.y))

    def render_shadow(self) -> None:
        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY30, [0, 0, self.width, 80])
        c = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
        for i in range(22):
            y = 80 + i * 2
            pygame.draw.line(c, (30, 30, 30, 255 - i * 12), (0, y), (self.width, y))
            pygame.draw.line(c, (30, 30, 30, 255 - i * 12), (0, y+1), (self.width, y+1))
        self.canvas.blit(c, (0, 0))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height
        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

        self.title_label.x = self.width // 2

        if height and self.language_dropdown.get_box_rect().bottom >= self.height - 10:
            self.language_dropdown.set_max_height(self.height - 10 - self.language_dropdown.get_box_rect().top)

    def update_language(self) -> None:
        self.title_label.set_text(self.language_manager.get_string("settings"))
        self.general_label.set_text(self.language_manager.get_string("general"))
        self.language_label.set_text(self.language_manager.get_string("language"))
        self.language_label2.set_text(self.language_manager.get_string("language_description"))
        self.catholic_events_label.set_text(self.language_manager.get_string("catholic_events"))
        self.show_catholic_events_label.set_text(self.language_manager.get_string("catholic_events_description"))
        self.fill_events_label.set_text(self.language_manager.get_string("filled_events"))
        self.fill_events_label2.set_text(self.language_manager.get_string("filled_events_description"))
        self.graphics_label.set_text(self.language_manager.get_string("graphics"))
        self.graphics_label2.set_text(self.language_manager.get_string("graphics_description"))
        self.account_label.set_text(self.language_manager.get_string("account"))
        self.auto_sync_label.set_text(self.language_manager.get_string("auto_sync"))
        self.auto_sync_label2.set_text(self.language_manager.get_string("auto_sync_description"))
        self.sync_button.label.set_text(self.language_manager.get_string("sync_calendars"))
        self.sign_out_button.label.set_text(self.language_manager.get_string("sign_out_all"))

        self.language_label2.font = Assets().font14
        self.catholic_events_label.font = Assets().font14
        self.fill_events_label2.font = Assets().font14
        self.graphics_label2.font = Assets().font14
        self.auto_sync_label2.font = Assets().font14
        self.language_label.font = Assets().font18
        self.catholic_events_label.font = Assets().font18
        self.fill_events_label.font = Assets().font18
        self.graphics_label.font = Assets().font18
        self.auto_sync_label.font = Assets().font18
        self.sync_button.label.font = Assets().font18
        self.sign_out_button.label.font = Assets().font18

        adjust_labels_font_size(self.get_ui_elements())

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
