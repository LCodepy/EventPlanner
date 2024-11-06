import pygame

from src.events.event import Event, MouseMotionEvent, MouseFocusChangedEvent, WindowMinimizedEvent, \
    WindowUnminimizedEvent
from src.ui.alignment import HorizontalAlignment, VerticalAlignment
from src.ui.colors import Colors, Color
from src.ui.padding import Padding
from src.ui.ui_object import UIObject
from src.utils.ui_debugger import UIDebugger


class Label(UIObject):

    def __init__(self, canvas: pygame.Surface = None, pos: (int, int) = None, size: (int, int) = None, text: str = "",
                 text_color: Color = Colors.BLACK, font: pygame.font.Font = None, bold: bool = True,
                 horizontal_text_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
                 vertical_text_alignment: VerticalAlignment = VerticalAlignment.CENTER,
                 padding: Padding = None, line_spacing: int = 2, wrap_text: bool = True) -> None:
        if canvas and pos and size:
            super().__init__(canvas, pos, padding)
            self.canvas = canvas
            self.x, self.y = pos
            self.width, self.height = size
            self.label_canvas = pygame.Surface(size, pygame.SRCALPHA)
        else:
            self.canvas = self.x = self.y = self.width = self.height = None

        self.text = text
        self.text_color = text_color
        self.font = font or pygame.font.SysFont("arial", 12)
        self.bold = bold
        self.horizontal_text_alignment = horizontal_text_alignment
        self.vertical_text_alignment = vertical_text_alignment
        self.padding = padding or Padding()
        self.line_spacing = line_spacing
        self.wrap_text = wrap_text

        self.text_end_pos = (self.x, self.y)

        self.lines = None
        self.hovering = False

        if self.width is not None:
            self.update_text()

    def update_text(self) -> None:
        self.text_end_pos = (self.x, self.y - self.font.render("A", self.bold, self.text_color).get_height() // 2)

        text = " \n ".join(self.text.split("\n"))
        words = list(filter(bool, text.split(" ")))
        self.lines = [""]

        if not self.wrap_text:
            cut = False
            for word in words:
                if word == "\n":
                    continue
                if self.font.render(self.lines[0] + word + "...", self.bold, self.text_color).get_width() < self.width:
                    self.lines[0] += word + " "
                else:
                    cut = True
            self.lines[0] = self.lines[0][:-1] + ("..." if cut else "")
            return

        line = 0
        for word in words:
            if word == "\n":
                self.lines[line] = self.lines[line][:-1]
                self.lines.append("")
                line += 1
                continue
            if (
                self.font.render(self.lines[line] + word, self.bold, self.text_color).get_width() > self.width and
                self.lines[line]
            ):
                self.lines[line] = self.lines[line][:-1]
                self.lines.append("")
                line += 1
            self.lines[line] += word + " "

        if len(text) > 0 and text[-1] != " ":
            self.lines[line] = self.lines[line][:-1]

    def set_text(self, text: str) -> None:
        self.text = text
        self.update_text()

    def post_init(self, canvas: pygame.Surface, pos: (int, int), size: (int, int)) -> None:
        self.canvas = canvas
        self.x, self.y = pos
        self.width, self.height = size
        super().__init__(canvas, pos, self.padding)

        self.label_canvas = pygame.Surface(size, pygame.SRCALPHA)

        self.text_end_pos = (self.x, self.y)

        self.update_text()

    def render(self) -> None:
        self.label_canvas.fill((0, 0, 0, 0))
        current_line_y = 0
        for text in self.lines:
            rendered = self.font.render(text, self.bold, self.text_color)

            if self.horizontal_text_alignment is HorizontalAlignment.LEFT:
                aligned_x = -self.width // 2 + self.padding.left
            elif self.horizontal_text_alignment is HorizontalAlignment.CENTER:
                aligned_x = -rendered.get_rect().w // 2
            elif self.horizontal_text_alignment is HorizontalAlignment.RIGHT:
                aligned_x = self.width // 2 - rendered.get_rect().w - self.padding.right
            else:
                raise ValueError("Invalid horizontal alignment.")

            if self.vertical_text_alignment is VerticalAlignment.BOTTOM or \
                (self.vertical_text_alignment is VerticalAlignment.CENTER and
                 len(self.lines) * (rendered.get_rect().h + self.line_spacing) > self.height):
                aligned_y = self.height // 2 - len(self.lines) * (rendered.get_rect().h + self.line_spacing) \
                            + current_line_y - self.padding.bottom
            elif self.vertical_text_alignment is VerticalAlignment.CENTER:
                aligned_y = -(len(self.lines) *
                              (rendered.get_rect().h + self.line_spacing) - self.line_spacing) // 2 + current_line_y
            elif self.vertical_text_alignment is VerticalAlignment.TOP:
                aligned_y = -self.height // 2 + current_line_y + self.padding.top
            else:
                raise ValueError("Invalid vertical alignment.")

            current_line_y += rendered.get_rect().h + self.line_spacing

            self.label_canvas.blit(rendered, (aligned_x + self.width // 2, aligned_y + self.height // 2))

            self.text_end_pos = (self.x + aligned_x + rendered.get_rect().w, self.y + aligned_y)

        self.canvas.blit(self.label_canvas, (self.x - self.width // 2, self.y - self.height // 2))

        # UI debugging
        if UIDebugger.is_enabled():
            pygame.draw.rect(self.canvas, UIDebugger.box_color, self.get_rect(), 1)
            pygame.draw.circle(self.canvas, UIDebugger.center_point_color, (self.x, self.y), 2)

    def register_event(self, event: Event) -> bool:
        if isinstance(event, MouseMotionEvent):
            currently_hovering = self.is_hovering((event.x, event.y))
            if currently_hovering != self.hovering:
                self.hovering = currently_hovering
                return True
        elif isinstance(event, WindowMinimizedEvent):
            self.hovering = False
            return True
        elif isinstance(event, WindowUnminimizedEvent):
            return True
        elif isinstance(event, MouseFocusChangedEvent):
            if self.hovering:
                self.hovering = event.focused
                return True
        return False

    def update_canvas(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas

    def get_text_end_pos(self) -> (int, int):
        return self.text_end_pos

    def get_text_height(self) -> int:
        return self.font.render("A", self.bold, self.text_color).get_rect().h

    def is_hovering(self, mouse_pos) -> bool:
        return self.get_rect().collidepoint(*mouse_pos)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    @staticmethod
    def render_text(canvas, text, pos, font, color, bold: bool = False,
                    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
                    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
                    alpha: int = -1):
        rendered = font.render(text, bold, color)

        if horizontal_alignment is HorizontalAlignment.LEFT:
            aligned_x = pos[0]
        elif horizontal_alignment is HorizontalAlignment.CENTER:
            aligned_x = pos[0] - rendered.get_rect().w // 2
        elif horizontal_alignment is HorizontalAlignment.RIGHT:
            aligned_x = pos[0] - rendered.get_rect().w
        else:
            raise ValueError("Invalid horizontal alignment.")

        if vertical_alignment is VerticalAlignment.TOP:
            aligned_y = pos[0]
        elif vertical_alignment is VerticalAlignment.CENTER:
            aligned_y = pos[0] - rendered.get_rect().h // 2
        elif vertical_alignment is VerticalAlignment.BOTTOM:
            aligned_y = pos[0] - rendered.get_rect().h
        else:
            raise ValueError("Invalid vertical alignment.")

        if alpha >= 0:
            transparent = pygame.Surface(rendered.get_size(), pygame.SRCALPHA)
            transparent.blit(rendered, (0, 0))
            transparent.set_alpha(alpha)
            canvas.blit(transparent, (aligned_x, aligned_y))
        else:
            canvas.blit(rendered, (aligned_x, aligned_y))

