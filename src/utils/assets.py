import os

import pygame

from src.utils.singleton import Singleton


class Assets(metaclass=Singleton):

    IMAGES_PATH = os.getcwd() + "\\assets\\images"
    DATA_PATH = os.getcwd() + "\\assets\\data"

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

        self.todo_list_icon_large = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "todo_list_icon_large.png")
        ).convert_alpha()
        self.todo_list_icon_large_hover = pygame.image.load(
            os.path.join(self.IMAGES_PATH, "todo_list_icon_large_hover.png")
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

        # Fonts
        self.font14 = pygame.font.SysFont("arial", 14)
        self.font18 = pygame.font.SysFont("arial", 18)
        self.font24 = pygame.font.SysFont("arial", 24)
        self.font32 = pygame.font.SysFont("arial", 32)
        self.font36 = pygame.font.SysFont("arial", 36)
