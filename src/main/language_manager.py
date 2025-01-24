import json
import os
from enum import Enum, auto
from typing import Union

from src.main.settings import Settings
from src.utils.singleton import Singleton


class Language(Enum):

    ENGLISH = auto()
    CROATIAN = auto()
    SPANISH = auto()
    GERMAN = auto()


class LanguageManager(metaclass=Singleton):

    LANGUAGES_PATH = os.getcwd() + "\\assets\\languages"

    def __init__(self, language: Language = Language.ENGLISH) -> None:
        self.language = language

        self.language_names = {
            "hrv": Language.CROATIAN,
            "eng": Language.ENGLISH,
            "esp": Language.SPANISH,
            "deu": Language.GERMAN
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

        self.language = language

    def get_string(self, key: str) -> Union[str, list[str]]:
        return self.strings[key]

    def get_language_name(self, language: Language = None) -> str:
        language = language or self.language
        for name, lang in self.language_names.items():
            if lang == language:
                return name

        raise ValueError(f"Language {language} is not supported")

