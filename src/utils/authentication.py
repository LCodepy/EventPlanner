import datetime
import os
from dataclasses import dataclass
from typing import Optional

from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource
from httplib2.error import ServerNotFoundError

from src.utils.assets import Assets


SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar"
]

PORTS = [i for i in range(8080, 8100)]
USED_PORTS = []


@dataclass
class User:

    email: str
    uri: str
    name: str


class GoogleAuthentication:

    @staticmethod
    def authenticate_new_user() -> Optional[User]:
        if not os.path.exists(Assets().google_credentials_file_path):
            return

        flow = InstalledAppFlow.from_client_secrets_file(Assets().google_credentials_file_path, scopes=SCOPES)
        try:
            flow.run_local_server(port=GoogleAuthentication.get_available_port(), timeout_seconds=300)
        except (Warning, AttributeError) as e:
            print(e)
            return

        service = build("oauth2", "v2", credentials=flow.credentials)
        user_info = service.userinfo().get().execute()
        email = user_info["email"]
        uri = user_info["picture"]
        name = ""
        if "name" in user_info:
            name = user_info["name"]

        with open(os.path.join(Assets().google_tokens_path, f"token_{email}.json"), 'w') as token:
            token.write(flow.credentials.to_json())

        return User(email, uri, name)

    @staticmethod
    def authenticate_user_with_token(email: str) -> Optional[User]:
        if not os.path.exists(Assets().google_credentials_file_path):
            return

        token_file = os.path.join(Assets().google_tokens_path, f"token_{email}.json")

        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes=SCOPES)
        except FileNotFoundError:
            return

        if not creds.valid and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                return

        service = build("oauth2", "v2", credentials=creds)
        try:
            user_info = service.userinfo().get().execute()
        except ServerNotFoundError as e:
            print(e)
            return

        email = user_info["email"]
        uri = user_info["picture"]
        name = ""
        if "name" in user_info:
            name = user_info["name"]

        with open(os.path.join(Assets().google_tokens_path, f"token_{email}.json"), "w") as token:
            token.write(creds.to_json())

        return User(email, uri, name)

    @staticmethod
    def initialize_service(email: str) -> Resource:
        token_file = os.path.join(Assets().google_tokens_path, f"token_{email}.json")
        creds = None

        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except (ValueError, FileNotFoundError):
            pass

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(Assets().google_credentials_file_path, SCOPES)
                creds = flow.run_local_server(port=GoogleAuthentication.get_available_port(), timeout_seconds=300)

                with open(token_file, "w") as token:
                    token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    @staticmethod
    def get_available_port() -> int:
        for port in PORTS:
            if port not in USED_PORTS:
                USED_PORTS.append(port)
                return port

