import json
import os
import sys
from pathlib import Path

import pygame

from src.utils.singleton import Singleton


class Assets(metaclass=Singleton):

    IMAGES_PATH = os.getcwd() + "\\assets\\images"
    DATA_PATH = os.getcwd() + "\\assets\\data"
    GOOGLE_PATH = os.getcwd() + "\\assets\\google"
    GOOGLE_TOKENS_PATH = os.getcwd() + "\\assets\\tokens"
    SETTINGS_PATH = os.getcwd() + "\\assets\\settings"

    def __init__(self) -> None:
        if getattr(sys, "frozen", False):
            self.IMAGES_PATH = Path(sys._MEIPASS).__str__() + "\\assets\\images"
            self.GOOGLE_PATH = Path(sys._MEIPASS).__str__() + "\\assets\\google"

            self.SETTINGS_PATH = os.path.join(os.getenv("LOCALAPPDATA"), "EventPlanner/settings")
            self.DATA_PATH = os.path.join(os.getenv("LOCALAPPDATA"), "EventPlanner/data")
            self.GOOGLE_TOKENS_PATH = os.path.join(os.getenv("LOCALAPPDATA"), "EventPlanner/tokens")

        # App Bar icons
        self.app_icon = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "app_icon.png")
        ).convert_alpha()

        self.close_window_icon = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "close_window_icon.png")
        ).convert_alpha()
        self.close_window_icon_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "close_window_icon_hover.png")
        ).convert_alpha()
        self.maximize_window_icon = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "maximize_window_icon.png")
        ).convert_alpha()
        self.shrink_window_icon = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "shrink_window_icon.png")
        ).convert_alpha()
        self.minimize_window_icon = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "minimize_window_icon.png")
        ).convert_alpha()

        # Task Bar icons
        self.profile_picture_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "profile_picture_icon_large.png")
        ).convert_alpha()
        self.profile_picture_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "profile_picture_icon_large_hover.png")
        ).convert_alpha()
        self.profile_picture_icon_400x400 = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "profile_picture_icon_400x400.png")
        ).convert_alpha()

        self.search_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "search_icon_large.png")
        ).convert_alpha()
        self.search_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "search_icon_large_hover.png")
        ).convert_alpha()

        self.todo_list_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "todo_list_icon_large.png")
        ).convert_alpha()
        self.todo_list_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "todo_list_icon_large_hover.png")
        ).convert_alpha()

        self.calendar_view_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "calendar_view_icon_large.png")
        ).convert_alpha()

        self.calendar_view_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "calendar_view_icon_large_hover.png")
        ).convert_alpha()

        self.settings_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "settings_icon_large.png")
        ).convert_alpha()
        self.settings_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "settings_icon_large_hover.png")
        ).convert_alpha()

        # TodoList Icons
        self.delete_task_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "delete_task_icon_large.png")
        ).convert_alpha()
        self.delete_task_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "delete_task_icon_large_hover.png")
        ).convert_alpha()
        self.edit_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "edit_icon_large.png")
        ).convert_alpha()
        self.edit_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "edit_icon_large_hover.png")
        ).convert_alpha()

        # Calendar icons
        self.right_arrow_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "right_arrow_icon_large.png")
        ).convert_alpha()
        self.right_arrow_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "right_arrow_icon_large_hover.png")
        ).convert_alpha()

        self.left_arrow_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "left_arrow_icon_large.png")
        ).convert_alpha()
        self.left_arrow_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "left_arrow_icon_large_hover.png")
        ).convert_alpha()

        self.delete_filled_event_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "delete_filled_event_icon_large.png")
        ).convert_alpha()

        self.checkmark_icon = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "checkmark_icon_large.png")
        ).convert_alpha()

        self.todo_list_database_path = os.path.join(self.DATA_PATH, "todo_lists")
        self.calendar_database_path = os.path.join(self.DATA_PATH, "calendars")
        self.settings_database_path = os.path.join(self.SETTINGS_PATH, "settings.json")

        if not os.path.exists(self.settings_database_path):
            settings = {
                "language": "eng",
                "current_id": {
                    "calendar": 0
                },
                "default_event_color": "#FF5400",
                "show_catholic_events": False,
                "catholic_event_color": "#544ACC",
                "current_user_email": None,
                "render_filled_events": False,
                "high_quality_graphics": True,
                "autosync": True
            }
            with open(self.settings_database_path, "w", encoding="utf-16") as file:
                json.dump(settings, file)

        self.google_credentials_file_path = os.path.join(self.GOOGLE_PATH, "credentials.json")

        self.user_profile_pictures = {None: self.profile_picture_icon_large}

        # Fonts
        self.font = "roboto"
        self.font4 = pygame.font.SysFont(self.font, 4)
        self.font6 = pygame.font.SysFont(self.font, 6)
        self.font8 = pygame.font.SysFont(self.font, 8)
        self.font10 = pygame.font.SysFont(self.font, 10)
        self.font12 = pygame.font.SysFont(self.font, 12)
        self.font14 = pygame.font.SysFont(self.font, 14)
        self.font16 = pygame.font.SysFont(self.font, 16)
        self.font18 = pygame.font.SysFont(self.font, 18)
        self.font20 = pygame.font.SysFont(self.font, 20)
        self.font24 = pygame.font.SysFont(self.font, 24)
        self.font32 = pygame.font.SysFont(self.font, 32)
        self.font36 = pygame.font.SysFont(self.font, 36)
        self.fonts = [
            self.font4, self.font6, self.font8, self.font10, self.font12, self.font16, self.font18, self.font20,
            self.font24, self.font32, self.font36
        ]
