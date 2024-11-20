from enum import Enum
from typing import Tuple

Color = Tuple[int, int, int]


class Colors:

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BACKGROUND_GREY22 = (22, 22, 22)
    BACKGROUND_GREY30 = (30, 30, 30)
    GREY70 = (70, 70, 70)
    GREY140 = (140, 140, 140)
    BLUE220 = (42, 82, 220)
    YELLOW220 = (200, 220, 50)


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
    return tuple(eval("0x" + s[i * 2:i * 2 + 2]) for i in range(1, 4))


def get_hex_color(color: Color) -> str:
    return hex(color[0]).zfill(2) + hex(color[1])[2:].zfill(2) + hex(color[2])[2:].zfill(2)
