import time

import pygame

from src.controllers.appbar_controller import AppbarController
from src.controllers.calendar_controller import CalendarController
from src.controllers.taskbar_controller import TaskbarController
from src.events.event import CloseWindowEvent, WindowResizeEvent, MouseFocusChangedEvent, WindowMoveEvent, \
    OpenViewEvent, CloseViewEvent, MouseClickEvent, MouseReleaseEvent, DeleteCharacterEvent, RenderCursorEvent, \
    ResizeViewEvent
from src.events.event_loop import EventLoop
from src.main.config import Config
from src.main.window_manager import WindowManager
from src.models.appbar_model import AppbarModel
from src.models.calendar_model import CalendarModel
from src.models.taskbar_model import TaskbarModel
from src.ui.colors import Colors
from src.utils.assets import Assets
from src.utils.language_manager import LanguageManager
from src.utils.logging import Log
from src.utils.pygame_utils import set_window_pos
from src.utils.ui_debugger import UIDebugger
from src.views.appbar_view import AppbarView
from src.views.calendar_view import CalendarView
from src.views.taskbar_view import TaskbarView
from src.main.view_manager import ViewManager


class Main:

    def __init__(self) -> None:
        pygame.init()

        self.config = Config()

        self.win = pygame.display.set_mode(self.config.window_size, pygame.NOFRAME | pygame.SRCALPHA)
        self.window_width, self.window_height = self.config.window_size
        pygame.display.set_caption(self.config.window_title)
        pygame.display.set_icon(Assets().app_icon)
        pygame.font.init()

        # Log.enable()
        # UIDebugger.enable()

        self.event_loop = EventLoop()
        self.event_loop.add_repeating_event(DeleteCharacterEvent, 0.05)
        self.event_loop.add_repeating_event(RenderCursorEvent, 0.4)

        self.running = False
        self.update_display = False
        self.render_all = False

        LanguageManager(self.event_loop)

        self.appbar_model = AppbarModel()
        self.appbar_view = AppbarView(self.win, self.appbar_model, self.win.get_width(), 30, 0, 0)
        AppbarController(self.appbar_model, self.appbar_view, self.event_loop)

        self.taskbar_model = TaskbarModel()
        self.taskbar_view = TaskbarView(self.win, self.taskbar_model, 60, self.win.get_height() - 30, 0, 30)
        self.taskbar_controller = TaskbarController(self.taskbar_model, self.taskbar_view, self.event_loop)

        self.calendar_model = CalendarModel()
        self.calendar_view = CalendarView(self.win, self.calendar_model, self.win.get_width() - self.taskbar_view.width,
                                          self.win.get_height() - self.appbar_view.height, self.taskbar_view.width,
                                          self.appbar_view.height)
        self.calendar_controller = CalendarController(self.calendar_model, self.calendar_view, self.event_loop)

        self.window_manager = WindowManager(self.event_loop, 5)
        self.view_manager = ViewManager(self.win, self.event_loop, self.appbar_view, self.taskbar_view, self.calendar_view)

    def start(self) -> None:
        self.running = True

        self.render_start()

        while self.running:
            self.event_loop.run()
            self.register_events()
            self.render()

            time.sleep(1 / self.config.fps)

        pygame.quit()

    def register_events(self) -> None:
        self.view_manager.reset_views()

        self.update_display = False
        self.render_all = False
        new_window_size = None
        new_window_pos = None
        while self.event_loop.has_events():
            event = self.event_loop.next()
            # Log.i("New event: " + str(event))

            if isinstance(event, WindowResizeEvent):
                new_window_size = (event.width, event.height)
                self.update_display = True
                Log.i("Registered window resize event: " + str(event))
            if isinstance(event, WindowMoveEvent):
                new_window_pos = (event.x, event.y)
                self.update_display = True
                Log.i("Registered window move event: " + str(event))

            if self.window_manager.register_event(event):
                event = MouseFocusChangedEvent(time.time(), False)

            if self.view_manager.register_events(event):
                self.update_display = True

            if isinstance(event, CloseWindowEvent):
                self.running = False
                break

        resized = (True, True)
        if new_window_size:
            resized = self.resize_window(new_window_size)

        if new_window_pos and resized[0]:
            set_window_pos(x=new_window_pos[0])
        if new_window_pos and resized[1]:
            set_window_pos(y=new_window_pos[1])

    def render(self) -> None:
        self.view_manager.render(self.update_display)

        if self.update_display:
            pygame.display.update()

    def render_start(self):
        self.win.fill(Colors.BLACK)

        self.view_manager.render(True)

        pygame.display.update()

    def resize_window(self, window_size: (int, int)) -> (bool, bool):
        resized = [True, True]
        if window_size[1] < self.view_manager.get_min_size()[1]:
            window_size = (window_size[0], self.view_manager.get_min_size()[1])
            resized[1] = False
        if window_size[0] < self.view_manager.get_min_size()[0]:
            window_size = (self.view_manager.get_min_size()[0], window_size[1])
            resized[0] = False

        if window_size == pygame.display.get_window_size():
            return resized

        self.win = pygame.display.set_mode(window_size, pygame.NOFRAME)

        self.view_manager.resize(window_size)

        return resized


if __name__ == "__main__":
    main = Main()
    main.start()
