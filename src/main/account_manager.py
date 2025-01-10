import json
import os
import time
from threading import Thread
from typing import Optional

import pygame
from google.auth.exceptions import RefreshError
from httplib2 import ServerNotFoundError

from src.controllers.calendar_controller import CalendarController
from src.events.event import Event, UserSignInEvent, OpenViewEvent, UserSignOutEvent
from src.events.event_loop import EventLoop
from src.main.settings import Settings
from src.models.calendar_model import CalendarModel
from src.utils.assets import Assets
from src.utils.authentication import User, GoogleAuthentication
from src.utils.singleton import Singleton
from src.utils.web_utils import download_image
from src.views.calendar_view import CalendarView


class AccountManager(metaclass=Singleton):

    def __init__(self, display: pygame.Surface = None, event_loop: EventLoop = None) -> None:
        self.display = display
        self.event_loop = event_loop

        self.current_account: Optional[User] = None
        self.accounts: list[User] = []

        self.load_accounts()
        self.load_current_account()

    def register_event(self, event: Event) -> bool:
        if isinstance(event, UserSignInEvent):
            self.current_account = event.user
            if event.user not in self.accounts:
                self.accounts.append(event.user)

            Assets().user_profile_pictures[self.current_account.email] = download_image(event.user.uri) or Assets().profile_picture_icon_400x400

            self.save_current_account()

            self.open_calendar_view(f"calendar_{self.current_account.email}")

        return False

    def load_accounts(self) -> None:
        accounts = os.listdir(Assets().google_tokens_path)
        for acc in accounts:
            user = GoogleAuthentication.authenticate_user_with_token(acc[6:-5])
            if user:
                self.accounts.append(user)
                Assets().user_profile_pictures[user.email] = download_image(user.uri) or Assets().profile_picture_icon_400x400

    def load_current_account(self) -> None:
        settings = Settings().get_settings()

        if not settings["current_user_email"]:
            return

        try:
            self.current_account = GoogleAuthentication.authenticate_user_with_token(settings["current_user_email"])
            if self.current_account is None:
                return
            Assets().user_profile_pictures[self.current_account.email] = download_image(self.current_account.uri) or Assets().profile_picture_icon_400x400
        except RefreshError:
            print("Error loading current account.")

    def save_current_account(self) -> None:
        if not self.current_account:
            return

        Settings().update_settings(["current_user_email"], self.current_account.email)

    def sign_in_user(self, email: str) -> None:
        def authenticate(on_complete):
            try:
                on_complete(GoogleAuthentication.authenticate_user_with_token(email))
            except ServerNotFoundError as e:
                print(e)

        def callback(user: User) -> None:
            if user is None:
                return
            self.event_loop.enqueue_threaded_event(UserSignInEvent(time.time(), user))

        Thread(target=authenticate, args=(callback,)).start()

    def sing_in_new_user(self) -> None:
        def authenticate(on_complete):
            on_complete(GoogleAuthentication.authenticate_new_user())

        def callback(user: User) -> None:
            if user is None:
                return
            self.event_loop.enqueue_threaded_event(UserSignInEvent(time.time(), user))

        Thread(target=authenticate, args=(callback,)).start()

    def sign_out_current_user(self) -> None:
        if self.current_account is None:
            return

        self.accounts.remove(self.current_account)

        token_path = os.path.join(Assets().google_tokens_path, f"token_{self.current_account.email}.json")
        calendar_path = os.path.join(Assets().calendar_database_path, f"calendar_{self.current_account.email}.db")
        todo_list_path = os.path.join(Assets().calendar_database_path, f"todo_list_{self.current_account.email}.db")

        if os.path.exists(token_path):
            os.remove(token_path)

        settings = Settings().get_settings()
        settings["current_id"].pop(f"calendar_{self.current_account.email}")
        Settings().save_settings(settings)

        self.event_loop.enqueue_event(UserSignOutEvent(time.time(), self.current_account))

        Assets().user_profile_pictures.pop(self.current_account.email)
        self.current_account = None

        self.open_calendar_view("calendar")

    def open_calendar_view(self, database_name: str) -> None:
        model = CalendarModel(database_name=database_name)
        view = CalendarView(self.display, model, self.display.get_width() - 60,
                            self.display.get_height() - 30, 60, 30)
        CalendarController(model, view, self.event_loop)
        self.event_loop.enqueue_event(OpenViewEvent(time.time(), view, False))

    def is_signed_in(self) -> bool:
        return self.current_account is not None

    def get_user_profile_picture(self, email: Optional[str]) -> pygame.Surface:
        return Assets().user_profile_pictures[email]

    def get_current_profile_picture(self) -> pygame.Surface:
        return self.get_user_profile_picture(self.current_account.email if self.current_account else None)

    def get_current_database_name(self) -> str:
        if self.current_account is None:
            return "calendar"
        return f"calendar_{self.current_account.email}"
