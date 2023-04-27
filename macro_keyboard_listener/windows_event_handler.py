import ctypes
import ctypes.wintypes
import logging
import os
import time

from win32api import OpenProcess
from win32process import GetWindowThreadProcessId, GetModuleFileNameEx
from macro_keyboard_configuration_management.configuration_manager import ConfigurationManager
from typing import Callable

EVENT_SYSTEM_DIALOGSTART = 0x0010
WINEVENT_OUTOFCONTEXT = 0x0000
EVENT_OBJECT_FOCUS = 0x8005

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)

timer = 0
last_executable = None


class WindowsEventHandler:
    def __init__(self, configuration_manager: ConfigurationManager, update_hotkeys: Callable) -> None:
        """Handles windows events when the foreground executable changes for automatic profile change
        :param configuration_manager:
        """
        self.configuration_manager = configuration_manager
        self.update_hotkeys = update_hotkeys

        ole32.CoInitialize(0)
        win_event_proc = WinEventProcType(self.create_callback())
        user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
        self.hook = user32.SetWinEventHook(
            EVENT_OBJECT_FOCUS,
            EVENT_OBJECT_FOCUS,
            None,
            win_event_proc,
            0,
            0,
            0x0003
        )
        if self.hook == 0:
            self.__get_logger().warning("SetWinEventHook failed")
            return
        self.__get_logger().info("WindowsEventHandler initialized")
        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.DispatchMessageW(msg)
        user32.UnhookWinEvent(self.hook)
        ole32.CoUninitialize()

    @staticmethod
    def __get_logger():
        return logging.getLogger()

    def create_callback(self) -> Callable:
        """Creates a callback for the foreground window change
        :return: Callable callback that changes configuration automatically
        """

        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            global timer, last_executable
            if time.time() - timer <= 1:
                self.__get_logger().info("WindowsEvent triggered but still on cooldown")
                return
            try:
                _, p = GetWindowThreadProcessId(hwnd)
                handle = OpenProcess(0x0410, False, p)
                exe = GetModuleFileNameEx(handle, 0)
                exe = exe.split("\\")[-1]
                if exe in os.getenv("EXE_LIST") and exe != last_executable:
                    process = exe.split('.')[0]
                    if self.configuration_manager.set_configuration_for_process(process):
                        self.update_hotkeys()
                        last_executable = exe
                        timer = time.time()
                        logging.info(f"WindowsEvent triggered and set configuration for {exe}")
            except Exception as e:
                self.__get_logger().warning(e)

        return callback
