import json
import os
import time
from typing import Optional

from google.auth.exceptions import RefreshError

from src.events.event import Event, UserSignInEvent
from src.utils.assets import Assets
from src.utils.authentication import User, GoogleAuthentication
from src.utils.singleton import Singleton
from src.utils.web_utils import download_image


class AccountManager(metaclass=Singleton):

    def __init__(self) -> None:
        self.current_account: Optional[User] = None
        self.accounts = []

        self.load_accounts()
        self.load_current_account()

    def register_event(self, event: Event) -> bool:
        if isinstance(event, UserSignInEvent):
            self.current_account = event.user
            if event.user.email not in self.accounts:
                self.accounts.append(event.user.email)

            Assets().user_profile_picture = download_image(event.user.uri) or Assets().profile_picture_icon_400x400

            self.save_current_account()

        return False

    def load_accounts(self) -> None:
        accounts = os.listdir(Assets().google_tokens_path)
        for acc in accounts:
            self.accounts.append(acc[6:-5])

    def load_current_account(self) -> None:
        with open(Assets().settings_database_path, "r", encoding="utf-16") as file:
            fjson = json.load(file)

        if not fjson["current_user_email"]:
            return

        try:
            self.current_account = GoogleAuthentication.authenticate_user_with_token(fjson["current_user_email"])
            if self.current_account is None:
                return
            Assets().user_profile_picture = download_image(self.current_account.uri) or Assets().profile_picture_icon_400x400
        except RefreshError:
            print("Error loading current account.")

    def save_current_account(self) -> None:
        if not self.current_account:
            return

        with open(Assets().settings_database_path, "r", encoding="utf-16") as file:
            fjson = json.load(file)

        fjson["current_user_email"] = self.current_account.email
        fjson["current_user_name"] = self.current_account.name
        fjson["current_user_uri"] = self.current_account.uri

        with open(Assets().settings_database_path, "w", encoding="utf-16") as file:
            json.dump(fjson, file)

