import json
import os
from enum import Enum, auto
from typing import Union

from src.main.settings import Settings
from src.utils.singleton import Singleton


class Language(Enum):

    AFRIKAANS = auto()
    CZECH = auto()
    DANISH = auto()
    GERMAN = auto()
    ENGLISH = auto()
    SPANISH = auto()
    FILIPINO = auto()
    FRENCH = auto()
    CROATIAN = auto()
    HUNGARIAN = auto()
    ITALIAN = auto()
    NORWEGIAN = auto()
    POLISH = auto()
    PORTUGUESE = auto()
    SLOVENIAN = auto()
    TURKISH = auto()


class LanguageManager(metaclass=Singleton):

    LANGUAGES_PATH = os.getcwd() + "\\assets\\languages"

    def __init__(self, language: Language = Language.ENGLISH) -> None:
        self.language = language

        self.language_names = {
            "afr": Language.AFRIKAANS,
            "czs": Language.CZECH,
            "dan": Language.DANISH,
            "deu": Language.GERMAN,
            "eng": Language.ENGLISH,
            "esp": Language.SPANISH,
            "flp": Language.FILIPINO,
            "fra": Language.FRENCH,
            "hrv": Language.CROATIAN,
            "hun": Language.HUNGARIAN,
            "ita": Language.ITALIAN,
            "nrw": Language.NORWEGIAN,
            "pol": Language.POLISH,
            "por": Language.PORTUGUESE,
            "slo": Language.SLOVENIAN,
            "tur": Language.TURKISH
        }

        self.repr_languages = {
            "afr": "Afrikaans",
            "czs": "Čeština",
            "dan": "Dansk",
            "deu": "Deutsch",
            "eng": "English (US)",
            "esp": "Español",
            "flp": "Filipino",
            "fra": "Français",
            "hrv": "Hrvatski",
            "hun": "Magyar",
            "ita": "Italiano",
            "nrw": "Norsk",
            "pol": "Polski",
            "por": "Português",
            "slo": "Slovenčina",
            "tur": "Türkçe"
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

    def get_language_name(self, language: Union[Language, str] = None) -> str:
        if isinstance(language, str):
            for name, lang in self.repr_languages.items():
                if lang == language:
                    return name

        language = language or self.language
        for name, lang in self.language_names.items():
            if lang == language:
                return name

        raise ValueError(f"Language {language} is not supported")

    def get_repr_languages(self) -> list[str]:
        return [self.repr_languages[k] for k in self.languages]

    def get_language_by_name(self, name: str) -> Language:
        if len(name) <= 3:
            return self.language_names[name]

        for key, lang in self.repr_languages.items():
            if lang == name:
                break

        return self.language_names[key]
