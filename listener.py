import keyboard
from typing import Callable, Any
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from enum import Enum
from configuration_manager import ConfigurationManager
from constants import PREFIX_ABBREVIATION, MACRO_KEYBOARD_FILE_TYPE, PREFIX_INTERNAL_FUNCTION, \
    PREFIX_NEXT, PREFIX_PREV


class FunctionType(Enum):
    MACRO = 0
    INTERNAL = 1
    ABBREVIATION = 2


class KeyFunction:
    def __init__(self, arg: Any, function_type=FunctionType.MACRO, callback=None) -> None:
        self.arg = arg
        self.type = function_type
        self.callback = callback

    def get_function(self) -> Callable:
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
        self.recording = False
        self.configuration_manager = ConfigurationManager()
        self.update_hotkeys(init=True)
        self.__observe()

    def update_hotkeys(self, init=False):
        if not init:
            keyboard.remove_all_hotkeys()
        for key, arg in self.configuration_manager.get_configuration().keys.items():
            if arg.startswith(PREFIX_INTERNAL_FUNCTION):
                def callback():
                    if arg.endswith(PREFIX_PREV):
                        self.configuration_manager.previous_configuration()
                    elif arg.endswith(PREFIX_NEXT):
                        self.configuration_manager.next_configuration()
                    self.update_hotkeys()
                function = KeyFunction(arg, FunctionType.INTERNAL, callback=callback)
            elif arg.startswith(PREFIX_ABBREVIATION):
                function = KeyFunction(arg.split(':')[-1], function_type=FunctionType.ABBREVIATION)
            else:
                function = KeyFunction(arg)
            keyboard.add_hotkey(key, function.get_function())

    def __observe(self) -> None:
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


class KeyboardEventHandler(FileSystemEventHandler):

    def __init__(self, macro_keyboard: MacroKeyboard) -> None:
        self.keyboard = macro_keyboard
        self.last_updated = 0
        super().__init__()

    def on_modified(self, event):
        if time.time() - self.last_updated <= 1:
            return
        if event.src_path.endswith(MACRO_KEYBOARD_FILE_TYPE):
            self.keyboard.configuration_manager.read_configuration()
            self.keyboard.update_hotkeys()
            self.last_updated = time.time()


MacroKeyboard()
