import ctypes
import time

import pygame

from src.controllers.appbar_controller import AppbarController
from src.controllers.resizing_controller import ResizingController
from src.controllers.taskbar_controller import TaskbarController
from src.controllers.todo_list_controller import TodoListController
from src.events.event import CloseWindowEvent, WindowResizeEvent, MouseFocusChangedEvent, WindowMoveEvent, \
    OpenViewEvent, CloseViewEvent, MouseClickEvent, MouseReleaseEvent, DeleteCharacterEvent, RenderCursorEvent
from src.events.event_loop import EventLoop
from src.main.config import Config
from src.models.appbar_model import AppbarModel
from src.models.taskbar_model import TaskbarModel
from src.models.todo_list_model import TodoListModel
from src.ui.colors import Colors
from src.utils.animations import ChangeValuesAnimation
from src.utils.assets import Assets
from src.utils.logging import Log
from src.utils.pygame_utils import set_window_pos
from src.utils.ui_debugger import UIDebugger
from src.views.appbar_view import AppbarView
from src.views.resizing_view import ResizingView
from src.views.taskbar_view import TaskbarView
from src.views.todo_list_view import TodoListView
from src.views.view import View


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

        self.appbar_model = AppbarModel()
        self.appbar_view = AppbarView(self.win, self.appbar_model, self.win.get_width(), 30)
        self.appbar_controller = AppbarController(self.appbar_model, self.appbar_view, self.event_loop)

        self.resizing_view = ResizingView(self.win, 5)
        self.resizing_controller = ResizingController(self.resizing_view, self.event_loop, self.appbar_controller)

        self.taskbar_model = TaskbarModel()
        self.taskbar_view = TaskbarView(self.win, self.taskbar_model, 60, self.win.get_height() - 30, y=30)
        self.taskbar_controller = TaskbarController(self.taskbar_model, self.taskbar_view, self.event_loop)

        self.screen_fog = pygame.Surface((self.window_width, self.window_height - self.appbar_view.height), pygame.SRCALPHA)
        self.screen_fog_animation = ChangeValuesAnimation("IncreaseScreenFog", self.event_loop, 0.4)

        self.top_view = None
        self.views: list[View] = [self.appbar_view, self.taskbar_view]

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
        for view in self.views:
            view.set_rendering(False)

        self.update_display = False
        self.render_all = False
        new_window_size = None
        new_window_pos = None
        while self.event_loop.has_events():
            event = self.event_loop.next()
            # Log.i("New event: " + str(event))

            if isinstance(event, CloseWindowEvent):
                self.running = False
                break
            if isinstance(event, WindowResizeEvent):
                new_window_size = (event.width, event.height)
                self.update_display = True
                Log.i("Registered window resize event: " + str(event))
            if isinstance(event, WindowMoveEvent):
                new_window_pos = (event.x, event.y)
                self.update_display = True
                Log.i("Registered window move event: " + str(event))
            if isinstance(event, OpenViewEvent):
                event.view.display = self.win
                if event.is_popup:
                    self.top_view = event.view
                    self.screen_fog_animation.start([0], [150])
                else:
                    self.views.append(event.view)
            if isinstance(event, CloseViewEvent):
                if event.view in self.views:
                    self.views.remove(event.view)
                elif event.view == self.top_view:
                    self.top_view = None
                    self.screen_fog_animation.start([150], [0])

            if self.resizing_view.register_event(event):
                event = MouseFocusChangedEvent(time.time(), False)
            if self.screen_fog_animation.register_event(event):
                self.update_display = True

            for view in self.views:
                if view.register_event(event):
                    self.update_display = True
                    view.set_rendering(True)
                    Log.i(f"Registered {event} on {view.__class__}")
                if isinstance(event, (MouseClickEvent, MouseReleaseEvent)) and view.is_focused(event) and self.top_view:
                    self.top_view = None
                    self.screen_fog_animation.start([150], [0])

            if self.top_view and self.top_view.register_event(event):
                self.update_display = True
                self.top_view.set_rendering(True)

        if new_window_size:
            self.resize_window(new_window_size)
        if new_window_pos:
            set_window_pos(*new_window_pos)

    def render(self) -> None:
        for view in self.views:
            if view.rendering or self.update_display:
                view.render()

        if self.screen_fog_animation.values:
            self.screen_fog.fill((0, 0, 0))
            self.screen_fog.set_alpha(self.screen_fog_animation.values[0])
            self.win.blit(self.screen_fog, (0, self.appbar_view.height))

        if self.top_view:
            self.top_view.render()

        if self.update_display:
            self.resizing_view.render()
            pygame.display.update()

    def render_start(self):
        self.win.fill(Colors.BLACK)

        for view in self.views:
            view.render()

        self.resizing_view.render()

        pygame.display.update()

    def resize_window(self, window_size: (int, int)) -> None:
        self.win = pygame.display.set_mode(window_size, pygame.NOFRAME)
        self.appbar_view.resize(width=window_size[0])
        for view in self.views:
            if isinstance(view, (TaskbarView, TodoListView, )):
                view.resize(height=window_size[1] - self.appbar_view.height)
        self.screen_fog = pygame.Surface((window_size[0], window_size[1] - self.appbar_view.height), pygame.SRCALPHA)


if __name__ == "__main__":
    main = Main()
    main.start()
