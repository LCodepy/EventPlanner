from dataclasses import dataclass


@dataclass
class Padding:

    top: int = 0
    bottom: int = 0
    left: int = 0
    right: int = 0
