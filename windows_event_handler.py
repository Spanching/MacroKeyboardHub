import ctypes
import ctypes.wintypes
import os
import time

import psutil
from win32api import OpenProcess
from win32process import GetWindowThreadProcessId, GetModuleFileNameEx
from configuration_manager import ConfigurationManager
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


class WindowsEventHandler:
    def __init__(self, configuration_manager: ConfigurationManager) -> None:
        """Handles windows events when the foreground executable changes for automatic profile change
        :param configuration_manager:
        """
        ole32.CoInitialize(0)
        win_event_proc = WinEventProcType(self.create_callback())
        user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
        self.configuration_manager = configuration_manager
        self.hook = user32.SetWinEventHook(
            EVENT_OBJECT_FOCUS,
            EVENT_OBJECT_FOCUS,
            None,
            win_event_proc,
            0,
            0,
            WINEVENT_OUTOFCONTEXT
        )
        if self.hook == 0:
            print('SetWinEventHook failed')
            return
        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.DispatchMessageW(msg)
        user32.UnhookWinEvent(self.hook)
        ole32.CoUninitialize()

    def create_callback(self) -> Callable:
        """Creates a callback for the foreground window change
        :return: Callable callback that changes configuration automatically
        """
        @staticmethod
        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            global timer
            if time.time() - timer <= 1:
                return
            t, p = GetWindowThreadProcessId(hwnd)
            if psutil.pid_exists(p):
                handle = OpenProcess(0x0410, False, p)
                exe = GetModuleFileNameEx(handle, 0)
                exe = exe.split("\\")[-1]
                if exe in os.getenv("EXE_LIST"):
                    self.configuration_manager.set_configuration_for_process(exe)
            timer = time.time()
        return callback
