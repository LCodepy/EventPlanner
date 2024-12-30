import io
import pygame
import requests


def download_image(uri: str) -> pygame.Surface:
    response = requests.get(uri)

    if response.status_code == 200:
        img_bytes = io.BytesIO(response.content)
        return pygame.image.load(img_bytes)
