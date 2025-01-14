import json
import os
import time
from enum import Enum, auto
from typing import Union

from src.events.event import LanguageChangedEvent
from src.events.event_loop import EventLoop
from src.main.settings import Settings
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

        self.language_names = {
            "hrv": Language.CROATIAN,
            "eng": Language.ENGLISH
        }

        self.languages = []
        self.strings = {}
        self.load_data()

        self.set_language(self.language)

    def load_data(self) -> None:
        self.language = self.language_names[Settings().get_settings()["language"]]
        self.languages = sorted(list(map(lambda l: l.split(".")[0], os.listdir(self.LANGUAGES_PATH))))

    def set_language(self, language: Union[Language, str]) -> None:
        if isinstance(language, Language):
            filename = self.get_language_name(language)
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

    def get_language_name(self, language: Language = None) -> str:
        language = language or self.language
        for name, lang in self.language_names.items():
            if lang == language:
                return name

        raise ValueError(f"Language {language} is not supported")

