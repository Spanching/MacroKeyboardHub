import customtkinter as ctk

from macro_keyboard_hub.titlebar import TitleBar

class Popup(ctk.CTkToplevel):
    
    def __init__(self, root, width, height, titlebar = True, fg_color = None, **kwargs):
        super().__init__(fg_color=fg_color, **kwargs)
        self.root = root
        self.width = width
        self.height = height
        # remove titlebar
        self.overrideredirect(True)
        if titlebar:
            titlebar = TitleBar(self, title="")
            titlebar.pack(fill="both")
        
        self._center()
        
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable
        
    def _center(self):
        # Calculate the center position of the main window
        self.root.update_idletasks()
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        popup_width = self.width
        popup_height = self.height
        popup_x = x + (width // 2) - (popup_width // 2)
        popup_y = y + (height // 2) - (popup_height // 2)

        # Set the position of the popup window
        self.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

    def _on_closing(self):
        self.grab_release()
        self.destroy()
