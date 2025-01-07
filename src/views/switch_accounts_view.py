from typing import Union, Callable

import pygame

from src.events.event import MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, Event, \
    MouseMotionEvent, LanguageChangedEvent, UserSignInEvent
from src.events.event_loop import EventLoop
from src.main.account_manager import AccountManager
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.image import Image
from src.ui.label import Label
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.assets import Assets
from src.main.language_manager import LanguageManager
from src.utils.authentication import User
from src.views.view import View


class AccountObject(UIObject):

    def __init__(self, canvas: pygame.Surface, pos: (int, int), size: (int, int), user: User) -> None:
        super().__init__(canvas, pos)
        self.x, self.y = pos
        self.width, self.height = size
        self.user = user

        self.button = Button(
            self.canvas, pos, size, color=Colors.BACKGROUND_GREY22, border_width=0, border_radius=4
        )
        self.name_label = Label(
            self.canvas, (self.x + 34, self.y - 8), (self.width - 32, self.height - 10), text=self.user.name,
            text_color=Colors.WHITE, font=Assets().font18, horizontal_text_alignment=HorizontalAlignment.LEFT
        )
        self.email_label = Label(
            self.canvas, (self.x + 34, self.y + 10), (self.width - 32, self.height - 10), text=self.user.email,
            text_color=(200, 200, 200), font=Assets().font14, horizontal_text_alignment=HorizontalAlignment.LEFT
        )
        self.profile_picture = Image(
            self.canvas, (self.x - self.width // 2 + 25, self.y),
            AccountManager().get_user_profile_picture(self.user.email), size=(34, 34),
            border_radius=17
        )

    def register_event(self, event: Event) -> bool:
        if self.button.register_event(event):
            return True

    def render(self) -> None:
        self.button.render()
        self.name_label.render()
        self.email_label.render()
        self.profile_picture.render()


class SwitchAccountsView(View):

    def __init__(self, display: pygame.Surface, event_loop: EventLoop, width: int, height: int, x: int, y: int) -> None:
        super().__init__(width, height, x, y)
        self.display = display
        self.event_loop = event_loop
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        self.rendering = False

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.shadow_canvas = pygame.Surface((self.width + 16, self.height + 16), pygame.SRCALPHA)

        self.language_manager = LanguageManager()

        self.account_list_pos = [self.width // 2, 100]
        self.on_create_accounts = None

        self.title_label = Label(
            self.canvas,
            (self.width // 2, 40),
            (self.width, 30),
            text="Choose Account",
            text_color=(200, 200, 200),
            font=Assets().font24
        )

        self.no_accounts_label = Label(
            self.canvas,
            (self.width // 2, self.height // 2),
            (self.width, 20),
            text="No accounts to show.",
            text_color=Colors.GREY140,
            font=Assets().font18
        )

        self.add_account_button = Button(
            self.canvas,
            (self.width // 2, self.height - 40),
            (self.width // 2 + 30, 40),
            label=Label(text="Add Account", text_color=(200, 200, 200), font=Assets().font18),
            border_width=1,
            border_radius=20,
            color=Colors.BACKGROUND_GREY30,
            border_color=Colors.GREY70,
            padding=Padding(left=10)
        )

        self.accounts: list[AccountObject] = []
        self.create_accounts()

    def register_event(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, MouseMotionEvent) and self.is_focused(event):
            registered_events = True
            if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif isinstance(event, (MouseClickEvent, MouseReleaseEvent, )) and self.is_focused(event):
            registered_events = True
        elif isinstance(event, LanguageChangedEvent):
            self.update_language()
        elif isinstance(event, UserSignInEvent):
            self.create_accounts()

        event = self.get_event(event)

        if self.add_account_button.register_event(event):
            registered_events = True

        for acc in self.accounts:
            if acc.register_event(event):
                registered_events = True

        return registered_events

    def render(self) -> None:
        self.canvas.fill((0, 0, 0, 0))

        pygame.draw.rect(self.canvas, Colors.BACKGROUND_GREY22, [0, 0, self.width, self.height], border_radius=4)
        pygame.draw.rect(self.canvas, Colors.GREY70, [0, 0, self.width, self.height], width=1, border_radius=4)

        self.title_label.render()
        if len(self.accounts) < 1:
            self.no_accounts_label.render()
        self.add_account_button.render()

        pygame.draw.line(self.canvas, (200, 200, 200), (self.add_account_button.get_rect().left + 12, self.add_account_button.y),
                         (self.add_account_button.get_rect().left + 26, self.add_account_button.y))
        pygame.draw.line(self.canvas, (200, 200, 200), (self.add_account_button.get_rect().left + 19, self.add_account_button.y - 7),
                         (self.add_account_button.get_rect().left + 19, self.add_account_button.y + 7))

        for acc in self.accounts:
            acc.render()

        self.shadow_canvas.fill((0, 0, 0, 0))
        for i in range(8):
            pygame.draw.rect(self.shadow_canvas, (0, 0, 0, max(70 - i * 9, 0)),
                             (8 - i, 0, self.width + 2*i, self.height + 2*i), border_radius=4 + 2*i, width=2)

        self.display.blit(self.shadow_canvas, (self.x-8, self.y))
        self.display.blit(self.canvas, (self.x, self.y))

    def create_accounts(self) -> None:
        accounts = AccountManager().accounts[:]
        if AccountManager().current_account:
            accounts.remove(AccountManager().current_account)

        self.accounts = [
            AccountObject(
                self.canvas, (self.width // 2, self.account_list_pos[1] + i * 50), (self.width - 20, 50),
                accounts[i]
            ) for i in range(len(accounts))
        ]
        if self.on_create_accounts:
            self.on_create_accounts()

    def resize(self, width: int = None, height: int = None) -> None:
        self.width = width or self.width
        self.height = height or self.height

        self.canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for obj in self.get_ui_elements():
            obj.update_canvas(self.canvas)

    def bind_on_create_accounts(self, callback: Callable) -> None:
        self.on_create_accounts = callback

    def update_language(self) -> None:
        pass

    def set_rendering(self, b: bool) -> None:
        self.rendering = b

    def is_focused(self, event: Union[MouseClickEvent, MouseReleaseEvent, MouseWheelUpEvent, MouseWheelDownEvent, MouseMotionEvent]) -> bool:
        return self.x <= event.x < self.x + self.width and self.y <= event.y < self.y + self.height

    def on_delete(self) -> None:
        pass

    def get_min_size(self) -> (int, int):
        return self.width, self.height
