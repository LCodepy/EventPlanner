import os

import pygame

from src.utils.singleton import Singleton


class Assets(metaclass=Singleton):

    IMAGES_PATH = os.getcwd() + "\\assets\\images"
    DATA_PATH = os.getcwd() + "\\assets\\data"
    GOOGLE_PATH = os.getcwd() + "\\assets\\google"

    def __init__(self) -> None:
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

        self.todo_list_database_path = os.path.join(self.DATA_PATH, "todo_list.db")

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

        self.calendar_database_path = os.path.join(self.DATA_PATH, "calendar.db")

        self.settings_database_path = os.path.join(self.DATA_PATH, "settings.json")

        self.google_credentials_file_path = os.path.join(self.GOOGLE_PATH, "credentials.json")
        self.google_tokens_path = os.path.join(self.GOOGLE_PATH, "tokens")

        self.user_profile_picture = self.profile_picture_icon_large

        # Fonts
        self.font = "roboto"
        self.font14 = pygame.font.SysFont(self.font, 14)
        self.font18 = pygame.font.SysFont(self.font, 18)
        self.font20 = pygame.font.SysFont(self.font, 20)
        self.font24 = pygame.font.SysFont(self.font, 24)
        self.font32 = pygame.font.SysFont(self.font, 32)
        self.font36 = pygame.font.SysFont(self.font, 36)
