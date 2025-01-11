from enum import Enum
from typing import Tuple

Color = Tuple[int, int, int]


class Colors:

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BACKGROUND_GREY10 = (10, 10, 10)
    BACKGROUND_GREY22 = (22, 22, 22)
    BACKGROUND_GREY30 = (30, 30, 30)
    GREY70 = (70, 70, 70)
    GREY140 = (140, 140, 140)
    BLUE220 = (42, 82, 220)
    YELLOW220 = (200, 220, 50)
    TEXT_GREY = (160, 160, 160)
    TEXT_LIGHT_GREY = (200, 200, 200)
    TEXT_DARK_GREY = (100, 100, 100)

    EVENT_GREEN204 = (112, 204, 0)
    EVENT_GREEN = (40, 100, 0)
    EVENT_BLUE = (0, 40, 204)
    EVENT_BLUE204 = (0, 102, 204)
    EVENT_PURPLE204 = (84, 70, 204)
    EVENT_PINK204 = (204, 48, 204)
    EVENT_RED204 = (204, 0, 50)
    EVENT_RED = (158, 0, 0)
    EVENT_ORANGE = (255, 84, 0)
    EVENT_YELLOW204 = (204, 170, 0)


def darken(color: Color, value: int):
    brighter = [*color]
    for i in range(3):
        brighter[i] = max(min(color[i] - value, 255), 0)
    return brighter[0], brighter[1], brighter[2]


def brighten(color: Color, value: int):
    brighter = [*color]
    for i in range(3):
        brighter[i] = max(min(color[i] + value, 255), 0)
    return brighter[0], brighter[1], brighter[2]


def get_rgb_color(s: str) -> Color:
    if s.startswith("#"):
        s = "0x" + s[1:]
    return tuple(eval("0x" + s[i * 2:i * 2 + 2]) for i in range(1, 4))


def get_hex_color(color: Color) -> str:
    return "0x" + hex(color[0])[2:].zfill(2) + hex(color[1])[2:].zfill(2) + hex(color[2])[2:].zfill(2)
