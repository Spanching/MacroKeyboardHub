import customtkinter as ctk
from PIL import Image
import keyboard
from macro_keyboard_configuration_management.configuration_manager import ConfigurationManager, KeyFunction, FunctionType
from macro_keyboard_configuration_management.constants import ABBREVIATION, BUTTON, INTERNAL_FUNCTION, CONFIG, RESET, ADD, DELETE, PREV, NEXT, CANCEL, EDIT, LOCK
from macro_keyboard_hub.popup.abbreviation_dialog import AbbreviationDialog
from macro_keyboard_hub.popup.confirmation_dialog import ConfirmationDialog
from macro_keyboard_hub.popup.popup import Popup
from macro_keyboard_hub.titlebar import TitleBar

class GUI:
    def __init__(self) -> None:
        """
        Initializes the GUI and creates the layout from the configuration manager
        """
        self.recording = False
        self.configuration_manager = ConfigurationManager()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.geometry("700x500")
        titlebar = TitleBar(self.root, title="Custom MacroKeyboard Hub")
        titlebar.pack(fill="both")
        self.root.resizable(True, True)

        self.create_widgets()
        self.update_buttons()

    def create_widgets(self):
        self.config_frame = ctk.CTkFrame(self.root)
        self.config_frame.pack(pady=10, padx=10, fill=ctk.X)

        self.prev_button = self.create_icon_button("icons/arrow_left.png", self.handle_prev_config)
        self.prev_button.pack(side=ctk.LEFT, padx=5)

        self.config_label = ctk.CTkLabel(self.config_frame, text=self.configuration_manager.get_configuration().name, font=('Helvetica', 20))
        self.config_label.pack(side=ctk.LEFT, expand=True, fill=ctk.X)

        self.add_button = self.create_icon_button("icons/plus_icon.png", self.handle_add_config)
        self.add_button.pack(side=ctk.RIGHT, padx=5)

        self.delete_button = self.create_icon_button("icons/delete_icon.png", self.handle_delete_config)
        self.delete_button.pack(side=ctk.RIGHT, padx=5)

        self.reset_button = self.create_icon_button("icons/reset_icon.png", self.handle_reset_config)
        self.reset_button.pack(side=ctk.RIGHT, padx=5)

        self.add_button = self.create_icon_button("icons/arrow_right.png", self.handle_next_config)
        self.add_button.pack(side=ctk.RIGHT, padx=5)

        self.keyboard_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.keyboard_frame.pack(padx = 10, pady = 10, fill=ctk.BOTH, expand=True)

        self.button_frames = [ctk.CTkFrame(self.keyboard_frame, fg_color="transparent") for _ in range(4)]
        for frame in self.button_frames:
            frame.pack(fill=ctk.BOTH, expand=True)

    def create_icon_button(self, image_path, command):
        image = Image.open(image_path)
        image = image.resize((24, 24))
        photo = ctk.CTkImage(image, size=(24,24))
        button = ctk.CTkButton(self.config_frame, image=photo, command=command, text="", width=24, height=24, corner_radius=10)
        return button

    def update_buttons(self):
        for frame in self.button_frames:
            for widget in frame.winfo_children():
                widget.destroy()

        function: KeyFunction
        for index, (key, function) in enumerate(self.configuration_manager.get_configuration().keys.items()):
            button = ctk.CTkButton(self.button_frames[index // 4], text=function.get_name(), command=lambda k=key: self.handle_button_event(k), 
                                   corner_radius=10, fg_color="#2E2E2E", hover_color="#3E3E3E", height=50)
            # button.grid(column=index%4, row=index//4, padx=5, pady=5)
            button.pack(side=ctk.LEFT, padx=5, pady=5, fill=ctk.BOTH, expand=True)

    def start(self) -> None:
        """Starts the GUI event loop
        """
        self.root.mainloop()

    def handle_button_event(self, key: str) -> None:
        """Handles the button presses for the keys of the MacroKeyboard
        :param key: the key for which the button was pressed
        """
        popup_window = self.create_edit_popup(key)
        self.root.wait_visibility(popup_window)
        self.root.wait_window(popup_window)
        self.update_buttons()

    def handle_prev_config(self):
        self.configuration_manager.previous_configuration()
        self.update_configuration_name_and_buttons()

    def handle_next_config(self):
        self.configuration_manager.next_configuration()
        self.update_configuration_name_and_buttons()

    def handle_add_config(self):
        config_name = ctk.CTkInputDialog(text="Input the name of the new configuration.", title="Input").get_input()
        if config_name:
            self.configuration_manager.add_new_configuration(config_name)
            self.update_configuration_name_and_buttons()

    def handle_delete_config(self):
        if ConfirmationDialog(self.root, 250, 150, title="", text=f"Are you sure you want to\ndelete configuration {self.configuration_manager.get_configuration().name}?", font=("Helvetica", 15)).get_confirmation():
            self.configuration_manager.delete_current_configuration()
            self.update_configuration_name_and_buttons()

    def handle_reset_config(self):
        self.configuration_manager.reset_current_config()
        self.update_configuration_name_and_buttons()

    def update_configuration_name_and_buttons(self):
        self.config_label.configure(text=self.configuration_manager.get_configuration().name)
        self.update_buttons()

    def record_macro(self, key: str) -> None:
        """Records a macro that will be set as function for the key the user is currently editing
        :param key: the key for which the macro should be set
        """
        def record() -> str:
            """Handles the keyboard event for recording macros
            :return: string representation of the pressed buttons
            """
            pressed = []
            key_list = []
            self.recording = True
            while True:
                event = keyboard.read_event(suppress=True)
                if event.event_type == "down":
                    if event.name not in pressed:
                        key_list.append(event.name)
                        pressed.append(event.name)
                elif event.event_type == "up":
                    pressed.remove(event.name)
                if not pressed:
                    arg = '+'.join(key_list)
                    return arg
        recording = record()
        function = KeyFunction(recording, FunctionType.MACRO)
        self.configuration_manager.update_key(key, function)

    def create_edit_popup(self, key: str) -> ctk.CTkToplevel:
        """Create the edit popup window for a key
        :param key: the key which was pressed to trigger the popup
        :return: ctk.CTkToplevel window for the popup
        """
        popup_window = Popup(self.root, 300, 250)
        
        title_label = ctk.CTkLabel(popup_window, text="Change Button Function:")
        title_label.pack(pady=5)
        
        current_function_label = ctk.CTkLabel(popup_window, font=("Helvetica", 20), text=self.configuration_manager.get_key_function(key).get_name())
        current_function_label.pack(pady=5)
        
        frame = ctk.CTkFrame(popup_window)
        frame.pack(fill=ctk.BOTH, expand=True, padx = 10, pady = 10)
        
        frame.grid_columnconfigure((0, 1), weight=1)
        frame.grid_rowconfigure((0, 1, 2), weight=1)

        edit_button = ctk.CTkButton(frame, text="Edit", command=lambda: self.handle_edit(key, popup_window))
        edit_button.grid(row = 0, column = 0, columnspan=2, sticky="nsew", padx=5, pady=5)

        abbreviation_button = ctk.CTkButton(frame, text="Abbreviation", command=lambda: self.create_abbreviation(key, popup_window))
        abbreviation_button.grid(row = 1, column = 0, sticky="nsew", padx=5, pady=5)

        lock_button = ctk.CTkButton(frame, text="Lock", command=lambda: self.handle_internal_function(key, LOCK, popup_window))
        lock_button.grid(row = 1, column = 1, sticky="nsew", padx=5, pady=5)
        
        prev_button = ctk.CTkButton(frame, text="Prev", command=lambda: self.handle_internal_function(key, PREV, popup_window))
        prev_button.grid(row = 2, column = 0, sticky="nsew", padx=5, pady=5)

        next_button = ctk.CTkButton(frame, text="Next", command=lambda: self.handle_internal_function(key, NEXT, popup_window))
        next_button.grid(row=2, column = 1, sticky="nsew", padx=5, pady=5)

        return popup_window

    def handle_edit(self, key: str, popup_window: ctk.CTkToplevel):
        self.record_macro(key)
        popup_window.destroy()
        self.update_buttons()

    def handle_internal_function(self, key: str, function_type: str, popup_window: ctk.CTkToplevel):
        function = KeyFunction(function_type, FunctionType.INTERNAL)
        self.configuration_manager.update_key(key, function)
        popup_window.destroy()
        self.update_buttons()

    def create_abbreviation(self, key: str, popup_window: ctk.CTkToplevel):
        name, abbreviation = AbbreviationDialog(self.root, 300, 300).get_input()
        if name and abbreviation:
            function = KeyFunction(abbreviation, FunctionType.ABBREVIATION, name=name)
            self.configuration_manager.update_key(key, function)
            popup_window.destroy()
            self.update_buttons()
        else:
            popup_window.destroy()

if __name__ == "__main__":
    gui = GUI()
    gui.start()