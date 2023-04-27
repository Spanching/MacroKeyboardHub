import logging
import os
import queue
from threading import Thread

import keyboard
from typing import Callable
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from enum import Enum
from macro_keyboard_configuration_management.configuration_manager import ConfigurationManager
from macro_keyboard_configuration_management.constants import ABBREVIATION, MACRO_KEYBOARD_FILE_TYPE, \
    INTERNAL_FUNCTION, NEXT, PREV, POPUP_PADDING
from macro_keyboard_listener.windows_event_handler import WindowsEventHandler
import PySimpleGUI as Psg
from win32api import GetMonitorInfo, MonitorFromPoint


class FunctionType(Enum):
    """The type of the Function for a key
    """
    MACRO = 0
    INTERNAL = 1
    ABBREVIATION = 2


class KeyFunction:
    """Represents the Function of a Key
    """

    def __init__(self, arg: str, function_type=FunctionType.MACRO, callback: Callable = None) -> None:
        self.arg = arg
        self.type = function_type
        self.callback = callback

    def get_function(self) -> Callable:
        """Prepares a function callable for the function this represents
        :return: Callable for the KeyFunction
        """
        if self.type == FunctionType.MACRO:
            return lambda: keyboard.press_and_release(self.arg)
        elif self.type == FunctionType.ABBREVIATION:
            return lambda: keyboard.write(self.arg)
        elif self.type == FunctionType.INTERNAL:
            return self.callback


class MacroKeyboard:
    def __init__(self) -> None:
        """Initializes the MacroKeyboard with its configuration manager and loads the functions from there
        """
        self.recording = False
        self.configuration_manager = ConfigurationManager()
        self.popup_queue = queue.Queue(maxsize=2)
        self.update_hotkeys(init=True)
        self.__observe()
        os.getenv("USE_FOREGROUND_WINDOW_DETECTION")
        if os.getenv("USE_FOREGROUND_WINDOW_DETECTION"):
            Thread(target=lambda: WindowsEventHandler(self.configuration_manager, self.update_hotkeys)).start()
        self.handle_queue()
        logging.info("MacroKeyboard initialized")

    def handle_queue(self):
        while True:
            while self.popup_queue.full():
                self.popup_queue.get()
            item = self.popup_queue.get()
            self.show_configuration_popup(item)

    def update_hotkeys(self, init=False) -> None:
        """Update the hotkeys for the keyboard package, used every time the configuration changes
        :param init: if it is the first initialization (throws error if no hotkey exists)
        """
        try:
            self.configuration_manager.get_configuration()
        except IndexError as ie:
            logging.warning(ie)
            return
        if not init:
            keyboard.remove_all_hotkeys()
        for key, arg in self.configuration_manager.get_configuration().keys.items():
            if arg.startswith(INTERNAL_FUNCTION):
                def callback():
                    if arg.endswith(PREV):
                        self.configuration_manager.previous_configuration()
                        self.update_hotkeys()
                    elif arg.endswith(NEXT):
                        self.configuration_manager.next_configuration()
                        self.update_hotkeys()

                function = KeyFunction(arg, FunctionType.INTERNAL, callback=callback)
            elif arg.startswith(ABBREVIATION):
                function = KeyFunction(arg.split(':')[-1], function_type=FunctionType.ABBREVIATION)
            else:
                function = KeyFunction(arg)
            keyboard.add_hotkey(key, function.get_function(), suppress=True)
        self.popup_queue.put(f"{self.configuration_manager.get_configuration().name}")
        logging.info("Hotkeys updated")

    @staticmethod
    def show_configuration_popup(name) -> None:
        """Shows a psg popup with the current configuration
            """
        layout = [
            [Psg.Text(f"Configuration changed to {name}", font="Arial", background_color="black")]
        ]
        window = Psg.Window("Macro Keyboard Hub", layout, use_default_focus=False, finalize=True, modal=True,
                            no_titlebar=True, auto_close=True, auto_close_duration=1, background_color="black",
                            element_padding=20, keep_on_top=True)
        screen_width, screen_height = GetMonitorInfo(MonitorFromPoint((0, 0))).get("Work")[2:4]
        win_width, win_height = window.size
        x, y = screen_width - win_width - POPUP_PADDING, screen_height - win_height - POPUP_PADDING
        window.move(x, y)
        window.read()

    def __observe(self) -> None:
        """Observes the current directory for changes, used to react to configuration changes made in the GUI
        """
        path = sys.argv[1] if len(sys.argv) > 1 else '.'
        event_handler = KeyboardEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=False)
        observer.start()


class KeyboardEventHandler(FileSystemEventHandler):

    def __init__(self, macro_keyboard: MacroKeyboard) -> None:
        """Handles Events observed by the watchdog observer
        :param macro_keyboard: The keyboard we want to apply changes to
        """
        self.keyboard = macro_keyboard
        self.last_updated = 0
        super().__init__()

    def on_modified(self, event: FileSystemEvent) -> None:
        """Triggered when a file or directory in this directory was modified
        :param event: the Modification Event triggered
        """
        if time.time() - self.last_updated <= 1:
            logging.info("Modification detected but still on cooldown")
            return
        if event.src_path.endswith(MACRO_KEYBOARD_FILE_TYPE):
            self.keyboard.configuration_manager.read_configuration()
            self.keyboard.update_hotkeys()
            self.last_updated = time.time()
            logging.info("Modification detected and updated")
