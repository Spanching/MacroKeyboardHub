from typing import Union, Tuple, Optional
import customtkinter as ctk

from macro_keyboard_hub.popup import Popup
from macro_keyboard_hub.titlebar import TitleBar

class ConfirmationDialog(Popup):
    """
    Dialog with extra window, message, entry widget, cancel and ok button.
    For detailed information check out the documentation.
    """

    def __init__(self,
                 root: ctk.CTkBaseClass,
                 width: int, height: int,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 title: str = "ConfirmationDialog",
                 font: Optional[Union[tuple, ctk.CTkFont]] = None,
                 text: str = "ConfirmationDialog", **kwargs):

        super().__init__(root, width, height, fg_color=fg_color, titlebar=False, **kwargs)

        self._confirmed: bool = False
        self._running: bool = False
        self._title = title
        self._text = text
        self._font = font
        
        self._create_widgets()

    def _create_widgets(self):
        
        frame = ctk.CTkFrame(self)
        frame.pack(fill=ctk.BOTH, expand=True)
        
        frame.grid_columnconfigure((0, 1), weight=1)
        frame.rowconfigure(0, weight=1)

        self._label = ctk.CTkLabel(master=frame,
                               width=300,
                               wraplength=300,
                               fg_color="transparent",
                               text=self._text,
                               font=self._font)
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._ok_button = ctk.CTkButton(master=frame,
                                    width=100,
                                    border_width=0,
                                    text='Ok',
                                    font=self._font,
                                    command=self._ok_event)
        self._ok_button.grid(row=1, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")

        self._cancel_button = ctk.CTkButton(master=frame,
                                        width=100,
                                        border_width=0,
                                        text='Cancel',
                                        font=self._font,
                                        command=self._cancel_event)
        self._cancel_button.grid(row=1, column=1, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew")

    def _ok_event(self, event=None):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def get_confirmation(self):
        self.master.wait_window(self)
        return self._confirmed
