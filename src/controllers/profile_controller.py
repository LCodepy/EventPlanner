import time
from threading import Thread

import pygame

from src.events.event import MouseMotionEvent, MouseClickEvent, MouseReleaseEvent, ResizeViewEvent, OpenViewEvent, \
    UserSignInEvent
from src.events.event_loop import EventLoop
from src.main.account_manager import AccountManager
from src.utils.authentication import GoogleAuthentication, User
from src.views.profile_view import ProfileView


class ProfileController:

    def __init__(self, view: ProfileView, event_loop: EventLoop) -> None:
        self.view = view
        self.event_loop = event_loop

        self.pressed = False
        self.last_frame_interacted = False

        self.view.bind_on_click(self.on_click)
        self.view.bind_on_release(self.on_release)
        self.view.bind_on_mouse_motion(self.on_mouse_motion)

        self.view.sign_in_button.bind_on_click(self.sign_in)

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
                ResizeViewEvent(time.time(), self.view, min(max(event.x, self.view.get_min_size()[0]), 550))
            )
            return True

    def sign_in(self) -> None:
        def authenticate(on_complete):
            on_complete(GoogleAuthentication.authenticate_new_user())

        def callback(user: User) -> None:
            self.event_loop.enqueue_threaded_event(UserSignInEvent(time.time(), user))

        Thread(target=authenticate, args=(callback, )).start()
