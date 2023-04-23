import PySimpleGUI as Psg
import keyboard
import re

from configuration_manager import ConfigurationManager
from constants import PREFIX_ABBREVIATION, PREFIX_BUTTON, \
    PREFIX_INTERNAL_FUNCTION, CONFIG_POSTFIX, PREFIX_RESET, PREFIX_ADD, PREFIX_DELETE, PREFIX_PREV, PREFIX_NEXT, \
    PREFIX_CANCEL, PREFIX_EDIT


class GUI:
    def __init__(self) -> None:
        self.recording = False
        Psg.theme("Dark Grey 15")
        self.configuration_manager = ConfigurationManager()

        button_lists = [[], [], [], []]
        for index, (key, value) in enumerate(self.configuration_manager.get_configuration().keys.items()):
            button_lists[index // 4].append(Psg.Button(self.get_display_arg(value), key=f"{PREFIX_BUTTON}_{key}", size=(12, 5)))
        layout = [
            [Psg.Button("<", key="PREV_CONFIG"),
             Psg.Text(self.configuration_manager.get_configuration().name, key="-TEXT-CONFIG-", expand_x=True, justification="center"),
             Psg.Button(">", key="NEXT_CONFIG"), Psg.Button("+", key="ADD_CONFIG"),
             Psg.Button("Delete", key="DELETE_CONFIG"),
             Psg.Button("Reset", key="RESET_CONFIG")],
            *button_lists
        ]
        self.window = Psg.Window("Macro Keyboard Hub", layout)

    def update_config_name(self):
        self.window["-TEXT-CONFIG-"](self.configuration_manager.get_configuration().name)

    def update_buttons(self):
        for key, arg in self.configuration_manager.get_configuration().keys.items():
            self.window[f"{PREFIX_BUTTON}_{key}"](self.get_display_arg(arg))

    def record(self) -> str:
        pressed = 0
        key_list = []
        self.recording = True
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type == "down":
                key_list.append(event.name)
                pressed = pressed + 1
            elif event.event_type == "up":
                pressed = pressed - 1
            if pressed == 0:
                arg = '+'.join(key_list)
                return arg

    def record_macro(self, window, key):
        recording = self.record()
        window[f"{PREFIX_BUTTON}_{key}"](self.get_display_arg(recording))
        self.configuration_manager.update_key(key, recording)

    @staticmethod
    def get_display_arg(arg: str) -> str:
        if arg.startswith(PREFIX_ABBREVIATION):
            _, name, value = re.split('_|:', arg)
            return f"Abbr: {name}"
        elif arg.startswith(PREFIX_INTERNAL_FUNCTION):
            _, name = arg.split("_")
            return name
        return arg.replace("+", " + ")

    def show_gui(self):
        # Create an event loop
        while True:
            event, _ = self.window.read()
            if event is not None:
                if event.endswith(CONFIG_POSTFIX):
                    if event.startswith(PREFIX_RESET):
                        self.configuration_manager.reset_current_config()
                        self.update_buttons()
                    elif event.startswith(PREFIX_ADD):
                        config_name = Psg.popup_get_text("Input the name of the new configuration.")
                        if config_name is not None:
                            self.configuration_manager.add_new_configuration(config_name)
                            self.update_config_name()
                            self.update_buttons()
                    elif event.startswith(PREFIX_DELETE):
                        self.configuration_manager.delete_current_configuration()
                        self.update_config_name()
                        self.update_buttons()
                    elif event.startswith(PREFIX_PREV):
                        self.configuration_manager.previous_configuration(popup=False)
                        self.update_config_name()
                        self.update_buttons()
                    elif event.startswith(PREFIX_NEXT):
                        self.configuration_manager.next_configuration(popup=False)
                        self.update_config_name()
                        self.update_buttons()
                elif event.startswith(PREFIX_BUTTON):
                    key = event.split("_")[-1]
                    popup_layout = [
                        [Psg.Text("Change Button Function:")],
                        [Psg.Text(self.configuration_manager.get_key_function(key), expand_x=True),
                         Psg.Button("Edit", key=f"{PREFIX_INTERNAL_FUNCTION}_{PREFIX_EDIT}", size=(6, 1))],
                        [Psg.Button("Abbreviation", key=f"{PREFIX_INTERNAL_FUNCTION}_{PREFIX_ABBREVIATION}",
                                    expand_x=True)],
                        [Psg.Button("Prev", key=f"{PREFIX_INTERNAL_FUNCTION}_{PREFIX_PREV}", expand_x=True),
                         Psg.Button("Next", key=f"{PREFIX_INTERNAL_FUNCTION}_{PREFIX_NEXT}", expand_x=True)],
                        [Psg.Button("Cancel", key=f"{PREFIX_INTERNAL_FUNCTION}_{PREFIX_CANCEL}", expand_x=True)]
                    ]
                    popup_window = Psg.Window("Change Button Function", layout=popup_layout, modal=True, finalize=True,
                                              grab_anywhere=True, keep_on_top=True, no_titlebar=True)
                    while True:
                        popup_event, _ = popup_window.read()
                        if popup_event.startswith(PREFIX_INTERNAL_FUNCTION):
                            if popup_event.endswith(PREFIX_PREV) or popup_event.endswith(PREFIX_NEXT):
                                self.configuration_manager.update_key(key, popup_event)
                                popup_window.close()
                                self.update_buttons()
                                break
                            elif popup_event.endswith(PREFIX_ABBREVIATION):
                                name = Psg.popup_get_text("Add Abbreviation Name", keep_on_top=True)
                                abbreviation = Psg.popup_get_text("Add Abbreviation", keep_on_top=True)
                                if name is not None and name != '' and abbreviation is not None \
                                        and abbreviation != '':
                                    self.configuration_manager.update_key(key, f"{PREFIX_ABBREVIATION}_{name}:{abbreviation}")
                                    popup_window.close()
                                    self.update_buttons()
                                else:
                                    popup_window.close()
                                break
                            elif popup_event.endswith(PREFIX_CANCEL):
                                popup_window.close()
                                break
                            elif popup_event.endswith(PREFIX_EDIT):
                                self.record_macro(self.window, key)
                                popup_window.close()
                                self.update_buttons()
                                break
                        else:
                            popup_window.close()
                            break
            if event == Psg.WIN_CLOSED:
                break

        self.window.close()


GUI().show_gui()
