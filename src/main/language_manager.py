import json
import os
import time
from enum import Enum, auto
from typing import Union

from src.events.event import LanguageChangedEvent
from src.events.event_loop import EventLoop
from src.utils.assets import Assets
from src.utils.singleton import Singleton


class Language(Enum):

    ENGLISH = auto()
    CROATIAN = auto()


class LanguageManager(metaclass=Singleton):

    LANGUAGES_PATH = os.getcwd() + "\\assets\\languages"

    def __init__(self, event_loop: EventLoop = None, language: Language = Language.ENGLISH) -> None:
        self.event_loop = event_loop
        self.language = language
        self.load_data()
        self.strings = {}

        self.set_language(self.language)

    def load_data(self) -> None:
        if not os.path.exists(Assets().settings_database_path):
            return

        with open(Assets().settings_database_path, encoding="utf-16") as file:
            self.language = json.load(file)["language"]

    def set_language(self, language: Union[Language, str]) -> None:
        if isinstance(language, Language):
            if language is Language.ENGLISH:
                filename = "eng"
            elif language is Language.CROATIAN:
                filename = "hrv"
            else:
                raise ValueError(f"Language {language} is not supported.")
        else:
            filename = language

        try:
            with open(os.path.join(self.LANGUAGES_PATH, filename + ".json"), encoding="utf-16") as file:
                self.strings = json.load(file)
        except (UnicodeDecodeError, UnicodeError):
            with open(os.path.join(self.LANGUAGES_PATH, filename + ".json")) as file:
                self.strings = json.load(file)

        self.event_loop.enqueue_event(LanguageChangedEvent(time.time()))

    def get_string(self, key: str) -> Union[str, list[str]]:
        return self.strings[key]

