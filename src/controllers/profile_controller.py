import time
from threading import Thread

import pygame

from src.controllers.switch_accounts_controller import SwitchAccountsController
from src.events.event import MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, ResizeViewEvent, OpenViewEvent, \
    UserSignInEvent, CalendarSyncEvent
from src.events.event_loop import EventLoop
from src.main.account_manager import AccountManager
from src.main.calendar_sync_manager import CalendarSyncManager
from src.main.config import Config
from src.utils.authentication import GoogleAuthentication, User
from src.views.profile_view import ProfileView
from src.views.switch_accounts_view import SwitchAccountsView


class ProfileController:

    def __init__(self, view: ProfileView, event_loop: EventLoop) -> None:
        self.view = view
        self.event_loop = event_loop

        self.pressed = False
        self.last_frame_interacted = False

        self.view.bind_on_click(self.on_click)
        self.view.bind_on_release(self.on_release)
        self.view.bind_on_mouse_motion(self.on_mouse_motion)

        self.view.sign_in_button.bind_on_click(self.on_sign_in)

        self.view.sync_button.bind_on_click(self.on_sync)
        self.view.switch_account_button.bind_on_click(self.on_switch_accounts)
        self.view.sign_out_button.bind_on_click(self.on_sign_out)

    def on_click(self, event: MouseClickEvent) -> None:
        if self.view.width - 5 < event.x < self.view.width and 0 < event.y < self.view.height:
            self.pressed = True

    def on_release(self, event: MouseReleaseEvent) -> None:
        self.pressed = False

    def on_mouse_motion(self, event: MouseMotionEvent) -> bool:
        if event.y < 0:
            if self.last_frame_interacted:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.last_frame_interacted = False
            return False
        if (
            pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_SIZEWE and
            (self.view.width - 5 < event.x < self.view.width or self.pressed)
        ):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            self.last_frame_interacted = True
        elif pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW and self.last_frame_interacted:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.last_frame_interacted = False

        if self.pressed:
            self.event_loop.enqueue_event(
                ResizeViewEvent(
                    time.time(), self.view, min(max(event.x, self.view.get_min_size()[0]), Config.side_view_max_width)
                )
            )
            return True

    def on_sign_in(self) -> None:
        if AccountManager().users:
            view = SwitchAccountsView(
                self.view.display, self.event_loop, *Config.switch_account_view_size,
                self.view.x + self.view.width // 2 - Config.switch_account_view_size[0] // 2,
                self.view.height // 2 - Config.switch_account_view_size[1] // 2
            )
            SwitchAccountsController(view, self.event_loop)
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, False))
        else:
            AccountManager().sing_in_new_user()

    def on_sign_out(self) -> None:
        AccountManager().sign_out_current_user()

    def on_sync(self) -> None:
        CalendarSyncManager().sync_calendars_threaded()

    def on_switch_accounts(self) -> None:
        view = SwitchAccountsView(
            self.view.display, self.event_loop, *Config.switch_account_view_size,
            self.view.x + self.view.width // 2 - Config.switch_account_view_size[0] // 2,
            self.view.height // 2 - Config.switch_account_view_size[1] // 2 + Config.appbar_height + 50
        )
        SwitchAccountsController(view, self.event_loop)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, False))
