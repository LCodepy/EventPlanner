import json
import os
import time
from threading import Thread
from typing import Optional

import pygame
from google.auth.exceptions import RefreshError

from src.events.event import Event, UserSignInEvent
from src.events.event_loop import EventLoop
from src.utils.assets import Assets
from src.utils.authentication import User, GoogleAuthentication
from src.utils.singleton import Singleton
from src.utils.web_utils import download_image


class AccountManager(metaclass=Singleton):

    def __init__(self, event_loop: EventLoop = None) -> None:
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

        return False

    def load_accounts(self) -> None:
        accounts = os.listdir(Assets().google_tokens_path)
        for acc in accounts:
            user = GoogleAuthentication.authenticate_user_with_token(acc[6:-5])
            if user:
                self.accounts.append(user)
                Assets().user_profile_pictures[user.email] = download_image(user.uri) or Assets().profile_picture_icon_400x400

    def load_current_account(self) -> None:
        with open(Assets().settings_database_path, "r", encoding="utf-16") as file:
            fjson = json.load(file)

        if not fjson["current_user_email"]:
            return

        try:
            self.current_account = GoogleAuthentication.authenticate_user_with_token(fjson["current_user_email"])
            if self.current_account is None:
                return
            Assets().user_profile_pictures[self.current_account.email] = download_image(self.current_account.uri) or Assets().profile_picture_icon_400x400
        except RefreshError:
            print("Error loading current account.")

    def save_current_account(self) -> None:
        if not self.current_account:
            return

        with open(Assets().settings_database_path, "r", encoding="utf-16") as file:
            fjson = json.load(file)

        fjson["current_user_email"] = self.current_account.email

        with open(Assets().settings_database_path, "w", encoding="utf-16") as file:
            json.dump(fjson, file)

    def sign_in_user(self, email: str) -> None:
        def authenticate(on_complete):
            on_complete(GoogleAuthentication.authenticate_user_with_token(email))

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
        if os.path.exists(token_path):
            os.remove(token_path)

        Assets().user_profile_pictures.pop(self.current_account.email)
        self.current_account = None

    def is_signed_in(self) -> bool:
        return self.current_account is not None

    def get_user_profile_picture(self, email: Optional[str]) -> pygame.Surface:
        return Assets().user_profile_pictures[email]

    def get_current_profile_picture(self) -> pygame.Surface:
        return self.get_user_profile_picture(self.current_account.email if self.current_account else None)
