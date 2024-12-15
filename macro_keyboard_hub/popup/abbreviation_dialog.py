from typing import Union, Tuple, Optional
import customtkinter as ctk

from macro_keyboard_hub.popup.popup import Popup
from macro_keyboard_hub.titlebar import TitleBar

class AbbreviationDialog(Popup):
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

        super().__init__(root, width, height, fg_color=fg_color, titlebar=True, **kwargs)

        self._user_input = (None, None)
        self._running: bool = False
        self._title = title
        self._text = text
        self._font = font
        
        self._create_widgets()

    def _create_widgets(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill=ctk.BOTH, expand=True, padx = 10, pady = 10)
        
        frame.grid_columnconfigure((0,1), weight=1)
        
        self._label = ctk.CTkLabel(master=frame,
                               fg_color="transparent",
                               text="Abbreviation Name:",
                               font=self._font)
        self._label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nw")

        self._entry_first = ctk.CTkEntry(master=frame,
                               width=230,
                               font=self._font)
        self._entry_first.grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 10), sticky="nw")
        
        self._label = ctk.CTkLabel(master=frame,
                               fg_color="transparent",
                               text="Abbreviation:",
                               font=self._font)
        self._label.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nw")

        self._entry_second = ctk.CTkEntry(master=frame,
                               width=230,
                               font=self._font)
        self._entry_second.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="nw")
        
        self._ok_button = ctk.CTkButton(master=frame,
                                    width=100,
                                    border_width=0,
                                    text='Ok',
                                    font=self._font,
                                    command=self._ok_event)
        self._ok_button.grid(row=4, column=1, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")
        
        self.after(150, lambda: self._entry_first.focus())  # set focus to entry with slight delay, otherwise it won't work
        self._entry_first.bind("<Return>", lambda _: self._entry_second.focus())
        self._entry_second.bind("<Return>", self._ok_event)
        
    def _ok_event(self, event=None):
        self._user_input = (self._entry_first.get(), self._entry_second.get())
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self._user_input
