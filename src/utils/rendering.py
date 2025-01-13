import pygame


def render_rounded_rect(s, color, rect, r):
    x1, y1 = rect.x, rect.y
    r2 = r - 2
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, rect.w, rect.h)

    pygame.draw.line(surface, color, (rect.left + r2, rect.top), (rect.right - r2 - 1, rect.top))
    pygame.draw.line(surface, color, (rect.left + r2, rect.bottom - 1), (rect.right - r2 - 1, rect.bottom - 1))
    pygame.draw.line(surface, color, (rect.left, rect.top + r2), (rect.left, rect.bottom - 1 - r2))
    pygame.draw.line(surface, color, (rect.right - 1, rect.top + r2), (rect.right - 1, rect.bottom - 1 - r2))

    for y in range(rect.top, rect.top + r + 1):
        for x in range(rect.left, rect.left + r + 1 - y):
            dist = ((rect.left + r - x) ** 2 + (rect.top + r - y) ** 2) ** 0.5
            if -1 <= dist - r <= 1:
                surface.set_at((x, y), (*color, (1 - abs(dist - r)) * 255))

    for y in range(rect.top, rect.top + r + 1):
        for x in range(rect.right - r + y, rect.right):
            dist = ((rect.right - 1 - r - x) ** 2 + (rect.top + r - y) ** 2) ** 0.5
            if -1 <= dist - r <= 1:
                surface.set_at((x, y), (*color, (1 - abs(dist - r)) * 255))

    for y in range(rect.bottom - r, rect.bottom):
        for x in range(rect.left, rect.left + r + 1 - rect.h + y):
            dist = ((rect.left + r - x) ** 2 + (rect.bottom - 1 - r - y) ** 2) ** 0.5
            if -1 <= dist - r <= 1:
                surface.set_at((x, y), (*color, (1 - abs(dist - r)) * 255))

    for y in range(rect.bottom - r, rect.bottom):
        for x in range(rect.right - r + rect.h - y, rect.right):
            dist = ((rect.right - 1 - r - x) ** 2 + (rect.bottom - 1 - r - y) ** 2) ** 0.5
            if -1 <= dist - r <= 1:
                surface.set_at((x, y), (*color, (1 - abs(dist - r)) * 255))

    s.blit(surface, (x1, y1))