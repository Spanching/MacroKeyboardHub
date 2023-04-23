import os
from threading import Thread

import keyboard
from typing import Callable
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from enum import Enum
from configuration_manager import ConfigurationManager
from constants import ABBREVIATION, MACRO_KEYBOARD_FILE_TYPE, INTERNAL_FUNCTION, \
    NEXT, PREV
from windows_event_handler import WindowsEventHandler
from dotenv import load_dotenv

load_dotenv()


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
            def internal_function():
                self.callback()
            return internal_function


class MacroKeyboard:
    def __init__(self) -> None:
        """Initializes the MacroKeyboard with its configuration manager and loads the functions from there
        """
        self.recording = False
        self.configuration_manager = ConfigurationManager()
        self.update_hotkeys(init=True)
        self.__init_env()
        if os.getenv("USE_FOREGROUND_WINDOW_DETECTION"):
            Thread(target=lambda: WindowsEventHandler(self.configuration_manager)).start()
        self.__observe()

    def update_hotkeys(self, init=False) -> None:
        """Update the hotkeys for the keyboard package, used every time the configuration changes
        :param init: if it is the first initialization (throws error if no hotkey exists)
        """
        if not init:
            keyboard.remove_all_hotkeys()
        for key, arg in self.configuration_manager.get_configuration().keys.items():
            if arg.startswith(INTERNAL_FUNCTION):
                def callback():
                    if arg.endswith(PREV):
                        self.configuration_manager.previous_configuration()
                    elif arg.endswith(NEXT):
                        self.configuration_manager.next_configuration()
                    self.update_hotkeys()
                function = KeyFunction(arg, FunctionType.INTERNAL, callback=callback)
            elif arg.startswith(ABBREVIATION):
                function = KeyFunction(arg.split(':')[-1], function_type=FunctionType.ABBREVIATION)
            else:
                function = KeyFunction(arg)
            keyboard.add_hotkey(key, function.get_function())

    def __observe(self) -> None:
        """Observes the current directory for changes, used to react to configuration changes made in the GUI
        """
        path = sys.argv[1] if len(sys.argv) > 1 else '.'
        event_handler = KeyboardEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    @staticmethod
    def __init_env() -> None:
        """Initializes the .env file if it does not exist
        """
        if os.path.isfile(".env"):
            return
        with open(".env", 'w') as env_file:
            env_file.writelines([
                'USE_FOREGROUND_WINDOW_DETECTION = False\n',
                'EXE_LIST = ["chrome.exe", "explorer.exe"]\n'
            ])


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
            return
        if event.src_path.endswith(MACRO_KEYBOARD_FILE_TYPE):
            self.keyboard.configuration_manager.read_configuration()
            self.keyboard.update_hotkeys()
            self.last_updated = time.time()


MacroKeyboard()
