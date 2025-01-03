from typing import Union, Callable

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, Event, \
    MouseMotionEvent, LanguageChangedEvent, UserSignInEvent
from src.events.event_loop import EventLoop
from src.events.mouse_buttons import MouseButtons
from src.main.account_manager import AccountManager
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.image import Image
from src.ui.label import Label
from src.utils.assets import Assets
from src.main.language_manager import LanguageManager
from src.views.view import View


class ProfileView(View):

    def __init__(self, display: pygame.Surface, event_loop: EventLoop, width: int, height: int,
                 x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
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

        self.sign_in_button = Button(
            self.canvas,
            (self.width // 2, self.height // 2),
            (self.width - 100, 40),
            label=Label(text=self.language_manager.get_string("sign_in"),
                        text_color=(160, 160, 160), font=Assets().font18),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            border_radius=4
        )

        self.profile_picture = Image(
            self.canvas,
            (self.width // 2, 100),
            AccountManager().get_current_profile_picture(),
            size=(96, 96),
            border_radius=48
        )

        self.name_label = Label(
            self.canvas,
            (self.width // 2, 180),
            (self.width, 40),
            text=AccountManager().current_account.name if AccountManager().current_account else "",
            text_color=(200, 200, 200),
            font=Assets().font24
        )

        self.email_label = Label(
            self.canvas,
            (self.width // 2, 220),
            (self.width, 30),
            text=AccountManager().current_account.email if AccountManager().current_account else "",
            text_color=(160, 160, 160),
            font=Assets().font18
        )

        self.sync_button = Button(
            self.canvas,
            (self.width // 2, 340),
            (200, 40),
            label=Label(text="Sync", text_color=(200, 200, 200), font=Assets().font18),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            border_radius=4
        )

        self.switch_account_button = Button(
            self.canvas,
            (self.width // 2, 400),
            (200, 40),
            label=Label(text="Switch Account", text_color=(200, 200, 200), font=Assets().font18),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            border_radius=4
        )

        self.sign_out_button = Button(
            self.canvas,
            (self.width // 2, 460),
            (200, 40),
            label=Label(text="Sign out", text_color=(200, 200, 200), font=Assets().font18),
            color=Colors.BACKGROUND_GREY22,
            border_width=0,
            border_radius=4
        )

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, LanguageChangedEvent):
            self.update_language()
        elif isinstance(event, UserSignInEvent):
            self.profile_picture.set_image(AccountManager().get_current_profile_picture())
            self.name_label.set_text(AccountManager().current_account.name)
            self.email_label.set_text(AccountManager().current_account.email)

        event = self.get_event(event)

        if self.get_state() == 0 and self.sign_in_button.register_event(event):
            registered_events = True
        elif self.get_state() == 1:
            if self.sync_button.register_event(event):
                registered_events = True
            if self.switch_account_button.register_event(event):
                registered_events = True
            if self.sign_out_button.register_event(event):
                registered_events = True

        if isinstance(event, MouseClickEvent) and self.on_click and event.button is MouseButtons.LEFT_BUTTON:
            self.on_click(event)
        elif isinstance(event, MouseReleaseEvent) and self.on_release and event.button is MouseButtons.LEFT_BUTTON:
            self.on_release(event)
        elif isinstance(event, MouseMotionEvent) and self.on_mouse_motion(event):
            return True

        return registered_events

    def render(self) -> None:
        self.canvas.fill(Colors.BACKGROUND_GREY30)

        if self.get_state() == 0:
            self.sign_in_button.render()
        elif self.get_state() == 1:
            self.profile_picture.render()
            self.name_label.render()
            self.email_label.render()
            self.sync_button.render()
            self.switch_account_button.render()
            self.sign_out_button.render()

        pygame.draw.line(self.canvas, Colors.GREY70, (self.width - 1, 0), (self.width - 1, self.height))

        self.display.blit(self.canvas, (self.x, self.y))

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

        self.sign_in_button.update_position(self.width // 2, self.height // 2)
        self.profile_picture.x = self.width // 2
        self.name_label.x = self.width // 2
        self.email_label.x = self.width // 2
        self.sync_button.update_position(self.width // 2)
        self.switch_account_button.update_position(self.width // 2)
        self.sign_out_button.update_position(self.width // 2)

    def update_language(self) -> None:
        pass

    def bind_on_click(self, on_click: Callable[[MouseClickEvent], None]) -> None:
        self.on_click = on_click

    def bind_on_release(self, on_release: Callable[[MouseReleaseEvent], None]) -> None:
        self.on_release = on_release

    def bind_on_mouse_motion(self, on_mouse_motion: Callable[[MouseMotionEvent], bool]) -> None:
        self.on_mouse_motion = on_mouse_motion

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_state(self) -> int:
        if AccountManager().current_account is None:
            return 0
        return 1

    def get_min_size(self) -> (int, int):
        return 150, 170
