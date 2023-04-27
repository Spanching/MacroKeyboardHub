import logging
import os
import queue
from threading import Thread

import keyboard
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from macro_keyboard_configuration_management.configuration_manager import ConfigurationManager, FunctionType, \
    KeyFunction
from macro_keyboard_configuration_management.constants import MACRO_KEYBOARD_FILE_TYPE, NEXT, PREV, POPUP_PADDING
from macro_keyboard_listener.windows_event_handler import WindowsEventHandler
import PySimpleGUI as Psg
from win32api import GetMonitorInfo, MonitorFromPoint


class MacroKeyboard:
    def __init__(self) -> None:
        """Initializes the MacroKeyboard with its configuration manager and loads the functions from there
        """
        self.recording = False
        self.configuration_manager = ConfigurationManager()
        self.popup_queue = queue.Queue(maxsize=2)
        self.update_hotkeys(init=True)
        self.__observe()
        if os.getenv("USE_FOREGROUND_WINDOW_DETECTION", "False").lower() == "true":
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
        for key, function in self.configuration_manager.get_configuration().keys.items():
            keyboard.add_hotkey(key, self.get_function_for_key_function(function), suppress=True)
        self.popup_queue.put(f"{self.configuration_manager.get_configuration().name}")
        logging.info("Hotkeys updated")

    def get_function_for_key_function(self, key_function: KeyFunction):
        if key_function.function_type == FunctionType.MACRO:
            return lambda: keyboard.press_and_release(key_function.arg)
        elif key_function.function_type == FunctionType.ABBREVIATION:
            return lambda: keyboard.write(key_function.arg)
        elif key_function.function_type == FunctionType.INTERNAL:
            def callback():
                if key_function.arg.endswith(PREV):
                    self.configuration_manager.previous_configuration()
                    self.update_hotkeys()
                elif key_function.arg.endswith(NEXT):
                    self.configuration_manager.next_configuration()
                    self.update_hotkeys()

            return callback

    @staticmethod
    def show_configuration_popup(name) -> None:
        """Shows a psg popup with the current configuration
            """
        if os.getenv("SHOW_POPUP", "False").lower() == "true":
            Psg.popup_auto_close(f"Configuration changed to {name}", font="Arial", background_color="black",
                                 button_type=Psg.POPUP_BUTTONS_NO_BUTTONS, no_titlebar=True)

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
