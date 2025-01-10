import json
from typing import Any

from src.utils.singleton import Singleton


class Settings(metaclass=Singleton):

    def __init__(self, file_path: str = None) -> None:
        self.file_path = file_path

    def update_settings(self, categories: list[str], value: Any) -> None:
        with open(self.file_path, "r", encoding="utf-16") as file:
            data = json.load(file)

        if len(categories) == 1:
            data[categories[0]] = value
        elif len(categories) == 2:
            data[categories[0]][categories[1]] = value
        else:
            raise ValueError("Too many subcategories (max 3).")

        with open(self.file_path, "w", encoding="utf-16") as file:
            json.dump(data, file)

    def get_settings(self) -> dict:
        with open(self.file_path, "r", encoding="utf-16") as file:
            return json.load(file)

    def save_settings(self, settings: dict) -> None:
        with open(self.file_path, "w", encoding="utf-16") as file:
            json.dump(settings, file)

