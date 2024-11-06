import ctypes
from ctypes import WINFUNCTYPE, POINTER, windll
from ctypes.wintypes import BOOL, HWND, RECT

import pygame


def get_window_pos() -> (int, int):
    hwnd = pygame.display.get_wm_info()["window"]
    prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
    paramflags = (1, "hwnd"), (2, "lprect")

    GetWindowRect = prototype(("GetWindowRect", windll.user32), paramflags)

    return GetWindowRect(hwnd).left, GetWindowRect(hwnd).top


def get_window_size() -> (int, int):
    working_area_rect = ctypes.wintypes.RECT()
    windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(working_area_rect), 0)
    return working_area_rect.right, working_area_rect.bottom


def set_window_pos(x: int = None, y: int = None) -> None:
    wx, wy = get_window_pos()
    ctypes.windll.user32.SetWindowPos(
        pygame.display.get_wm_info()['window'], None,
        wx if x is None else x, wy if y is None else y, 0, 0, 0x0001
    )
