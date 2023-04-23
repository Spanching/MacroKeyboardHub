import PySimpleGUI as Psg
import keyboard
import re

from configuration_manager import ConfigurationManager
from constants import ABBREVIATION, BUTTON, \
    INTERNAL_FUNCTION, CONFIG, RESET, ADD, DELETE, PREV, NEXT, \
    CANCEL, EDIT


class GUI:
    def __init__(self) -> None:
        """
        Initializes the GUI and creates the layout from the configuration manager
        """
        self.recording = False
        Psg.theme("Dark Grey 15")
        self.configuration_manager = ConfigurationManager()

        button_lists = [[], [], [], []]
        for index, (key, value) in enumerate(self.configuration_manager.get_configuration().keys.items()):
            button_lists[index // 4].append(
                Psg.Button(self.__get_display_arg(value), key=f"{BUTTON}_{key}", size=(12, 5)))
        layout = [
            [Psg.Button("<", key=f"{PREV}_{CONFIG}"),
             Psg.Text(self.configuration_manager.get_configuration().name, key="NAME_CONFIG", expand_x=True,
                      justification="center"),
             Psg.Button(">", key=f"{NEXT}_{CONFIG}"), Psg.Button("+", key="ADD_CONFIG"),
             Psg.Button("Delete", key=f"{DELETE}_{CONFIG}"),
             Psg.Button("Reset", key=f"{RESET}_{CONFIG}")],
            *button_lists
        ]
        self.window = Psg.Window("Macro Keyboard Hub", layout)

    def start(self) -> None:
        """Starts the GUI event loop
        """
        while True:
            event, _ = self.window.read()
            if event is not None:
                if event.endswith(CONFIG):
                    self.__handle_config_event(event)
                elif event.startswith(BUTTON):
                    self.__handle_button_event(event)
            if event == Psg.WIN_CLOSED:
                break

        self.window.close()

    def __update_config_name(self) -> None:
        """Update the name of the configuration on the top of the window
        """
        self.window["NAME_CONFIG"](self.configuration_manager.get_configuration().name)

    def __update_buttons(self) -> None:
        """Update the text on the Buttons
        """
        for key, arg in self.configuration_manager.get_configuration().keys.items():
            self.window[f"{BUTTON}_{key}"](self.__get_display_arg(arg))

    def __record_macro(self, window: Psg.Window, key: str) -> None:
        """Records a macro that will be set as function for the key the user is currently editing
        :param window: the psg window that contains the Buttons
        :param key: the key for which the macro should be set
        """
        recording = self.__record()
        window[f"{BUTTON}_{key}"](self.__get_display_arg(recording))
        self.configuration_manager.update_key(key, recording)

    def __record(self) -> str:
        """Handles the keyboard event for recording macros
        :return: string representation of the pressed buttons
        """
        pressed = []
        key_list = []
        self.recording = True
        while True:
            event = keyboard.read_event(suppress=True)
            print(event.name)
            if event.event_type == "down":
                if event.name not in pressed:
                    key_list.append(event.name)
                    pressed.append(event.name)
            elif event.event_type == "up":
                pressed.remove(event.name)
            if not pressed:
                arg = '+'.join(key_list)
                return arg

    def __handle_button_event(self, event: str) -> None:
        """Handles the button presses for the keys of the MacroKeyboard
        :param event: the psg event that happened last
        """
        key = event.split("_")[-1]
        popup_window = self.__create_popup(key)
        while True:
            popup_event, _ = popup_window.read()
            if popup_event.startswith(INTERNAL_FUNCTION):
                if popup_event.endswith(PREV) or popup_event.endswith(NEXT):
                    self.configuration_manager.update_key(key, popup_event)
                    self.__close_popup_update(popup_window)
                    break
                elif popup_event.endswith(ABBREVIATION):
                    self.__create_abbreviation(key, popup_window)
                    break
                elif popup_event.endswith(CANCEL):
                    popup_window.close()
                    break
                elif popup_event.endswith(EDIT):
                    self.__record_macro(self.window, key)
                    self.__close_popup_update(popup_window)
                    break
            else:
                popup_window.close()
                break

    def __create_abbreviation(self, key: str, popup_window: Psg.Window) -> None:
        """Handles the creation of an Abbreviation for a key
        :param key: the key that will hold this abbreviation
        :param popup_window: the window that handles editing the function for the pressed key
        """
        name = Psg.popup_get_text("Add Abbreviation Name", keep_on_top=True, no_titlebar=True)
        abbreviation = Psg.popup_get_text("Add Abbreviation", keep_on_top=True, no_titlebar=True)
        if name is not None and name != '' and abbreviation is not None \
                and abbreviation != '':
            self.configuration_manager.update_key(key, f"{ABBREVIATION}_{name}:{abbreviation}")
            self.__close_popup_update(popup_window)
        else:
            popup_window.close()

    def __create_popup(self, key: str) -> Psg.Window:
        """Create the edit popup window for a key
        :param key: the key which was pressed to trigger the popup
        :return: psg window for the popup
        """
        popup_layout = [
            [Psg.Text("Change Button Function:")],
            [Psg.Text(self.configuration_manager.get_key_function(key), expand_x=True),
             Psg.Button("Edit", key=f"{INTERNAL_FUNCTION}_{EDIT}", size=(6, 1))],
            [Psg.Button("Abbreviation", key=f"{INTERNAL_FUNCTION}_{ABBREVIATION}",
                        expand_x=True)],
            [Psg.Button("Prev", key=f"{INTERNAL_FUNCTION}_{PREV}", expand_x=True),
             Psg.Button("Next", key=f"{INTERNAL_FUNCTION}_{NEXT}", expand_x=True)],
            [Psg.Button("Cancel", key=f"{INTERNAL_FUNCTION}_{CANCEL}", expand_x=True)]
        ]
        popup_window = Psg.Window("Change Button Function", layout=popup_layout, modal=True, finalize=True,
                                  grab_anywhere=True, keep_on_top=True, no_titlebar=True)
        return popup_window

    def __close_popup_update(self, popup_window: Psg.Window) -> None:
        """Helper for closing the popup and updating all the buttons with their function
        :param popup_window: the window for the editing popup that should be closed
        """
        popup_window.close()
        self.__update_buttons()

    def __handle_config_event(self, event: str) -> None:
        """Handles configuration events for adding, resetting, deletion of a configuration
        :param event: the psg event that happened last
        :return:
        """
        if event.startswith(RESET):
            self.configuration_manager.reset_current_config()
            self.__update_buttons()
        elif event.startswith(ADD):
            config_name = Psg.popup_get_text("Input the name of the new configuration.")
            if config_name is not None:
                self.configuration_manager.add_new_configuration(config_name)
                self.__update_config_name()
                self.__update_buttons()
        elif event.startswith(DELETE):
            self.configuration_manager.delete_current_configuration()
            self.__update_config_name()
            self.__update_buttons()
        elif event.startswith(PREV):
            self.configuration_manager.previous_configuration(popup=False)
            self.__update_config_name()
            self.__update_buttons()
        elif event.startswith(NEXT):
            self.configuration_manager.next_configuration(popup=False)
            self.__update_config_name()
            self.__update_buttons()

    @staticmethod
    def __get_display_arg(arg: str) -> str:
        """Gives a nicer representation for the function of a key
        :param arg: the raw function
        :return: nice string representation for the function
        """
        if arg.startswith(ABBREVIATION):
            _, name, value = re.split('[_:]', arg)
            return f"Abbr: {name}"
        elif arg.startswith(INTERNAL_FUNCTION):
            _, name = arg.split("_")
            return name
        return arg.replace("+", " + ")


GUI().start()
