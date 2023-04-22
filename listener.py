import os
import keyboard
from typing import Callable, Any
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent, FileSystemEventHandler

FILE_NAME = "configuration.mkc"

class KeyboardEventHandler(FileSystemEventHandler):

    def __init__(self, keyboard) -> None:
        self.keyboard = keyboard
        self.last_updated = 0
        super().__init__()
    
    def on_modified(self, event):
        if time.time() - self.last_updated <= 1:
            return
        if event.src_path.endswith(".mkc"):
            self.keyboard.update_hotkeys()
            self.last_updated = time.time()

class KeyFunction:
    def __init__(self, arg: Any) -> None:
        self.arg = arg

    def get_function(self) -> Callable:
        return lambda: keyboard.press_and_release(self.arg)

class MacroKeyboard:
    def __init__(self) -> None:
        self.recording = False
        self.hotkey_dict = {}
        if not self.__exists_valid_config():
            self.__init_config()
        self.update_hotkeys(init=True)
        self.__observe()
    
    def update_hotkeys(self, init = False):
        if not init:
            keyboard.remove_all_hotkeys()
        with open(FILE_NAME, "r") as file:
            lines = file.readlines()
            for line in lines:
                key, arg = line.strip().split(',')
                function = KeyFunction(arg)
                self.hotkey_dict[key] = function
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

    def __exists_valid_config(self) -> bool:
        if not os.path.isfile(FILE_NAME):
            return False
        with open(FILE_NAME, "r") as file:
            lines = file.readlines()
            if len(lines) != 16:
                return False
            for line in lines:
                if not ',' in line:
                    return False
        return True
    
    def __init_config(self) -> None:
        lines = ['f13,f13\n',
            'f14,f14\n',
            'f15,f15\n',
            'f16,f16\n',
            'f17,f17\n',
            'f18,f18\n',
            'f19,f19\n',
            'f20,f20\n',
            'strg+f13,strg+f13\n',
            'strg+f14,strg+f14\n',
            'strg+f15,strg+f15\n',
            'strg+f16,strg+f16\n',
            'strg+f17,strg+f17\n',
            'strg+f18,strg+f18\n',
            'strg+f19,strg+f19\n',
            'strg+f20,strg+f20\n',
        ]
        with open(FILE_NAME, "w") as file:
            file.writelines(lines)
    
MacroKeyboard()