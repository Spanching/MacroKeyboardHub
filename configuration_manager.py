import json
import os
from typing import Dict
import PySimpleGUI as Psg
from win32api import GetMonitorInfo, MonitorFromPoint

from constants import DEFAULT_FILE_NAME, DEFAULT_CONFIG_KEYS, POPUP_PADDING


class Configuration:
    def __init__(self, name: str, key_dict: Dict) -> None:
        """Represents a configuration for the MacroKeyboard
        :param name: the name of this representation
        :param key_dict: the mapping of keys to their function
        """
        self.name = name
        self.keys = key_dict


class ConfigurationManager:

    def __init__(self):
        """Handles persistence of Configurations and changes, used by GUI and Listener without synchronization of
        indices, but with synchronized configurations
        """
        self.configurations = []
        self.configuration_index = 0
        if self.__exists_valid_config():
            self.read_configuration()
        else:
            self.__init_config()

    def set_configuration_for_process(self, process: str) -> bool:
        """Sets configuration when foreground executable changes
        :param process: the name of the process that is now in the foreground
        """
        name = process.split(".")[0]
        for index, config in enumerate(self.configurations):
            if config.name == name:
                if self.configuration_index != index:
                    self.configuration_index = index
                    self.__show_configuration_popup()
                    return True
        return False

    def read_configuration(self) -> None:
        """Reads the configuration file and updates the configurations list
        """
        self.configurations.clear()
        with open(DEFAULT_FILE_NAME, "r") as file:
            configs: Dict = json.load(file)
            for name in configs.keys():
                self.configurations.append(
                    Configuration(name=name, key_dict=configs[name])
                )

    def get_configuration(self) -> Configuration:
        """Returns the currently active configuration for this instance
        :return: Configuration that is currently active
        """
        return self.configurations[self.configuration_index]

    def next_configuration(self, popup=True) -> None:
        """Increments the index for the configurations
        :param popup: if to display a popup (only wanted for changes from the keyboard itself)
        """
        if len(self.configurations) > 1:
            self.configuration_index = (self.configuration_index + 1) % len(self.configurations)
            if popup:
                self.__show_configuration_popup()

    def previous_configuration(self, popup=True) -> None:
        """Decrements the index for the configurations
        :param popup: if to display a popup (only wanted for changes from the keyboard itself)
        """
        if len(self.configurations) > 1:
            self.configuration_index = (self.configuration_index - 1) % len(self.configurations)
            if popup:
                self.__show_configuration_popup()

    # GUI Functions
    def add_new_configuration(self, name: str) -> None:
        """Adds a new configuration with the default function mapping
        :param name: the name for the new configuration
        """
        self.configurations.append(
            Configuration(name=name, key_dict=DEFAULT_CONFIG_KEYS)
        )
        self.configuration_index = len(self.configurations) - 1
        self.__save_configurations()

    def delete_current_configuration(self) -> None:
        """Deletes the currently active Configuration
        """
        if len(self.configurations) > 1:
            self.configurations.pop(self.configuration_index)
            self.configuration_index = (self.configuration_index - 1) % len(self.configurations)
            self.__save_configurations()

    def get_key_function(self, key: str) -> str:
        """Returns the function for a key
        :param key: the key we want the function for
        :return: string representation of the key function
        """
        return self.configurations[self.configuration_index].keys[key]

    def update_key(self, key: str, arg: str) -> None:
        """Updates the function for a given key
        :param key: the key to update the function for
        :param arg: the new function represented as string
        """
        self.configurations[self.configuration_index].keys[key] = arg
        self.__save_configurations()

    def reset_current_config(self) -> None:
        """Resets the currently active configuration to the default function mapping
        """
        self.configurations[self.configuration_index].keys = DEFAULT_CONFIG_KEYS
        self.__save_configurations()

    def __show_configuration_popup(self) -> None:
        """Shows a psg popup with the current configuration
        """
        layout = [
            [Psg.Text(f"Configuration changed to {self.configurations[self.configuration_index].name}", font="Arial",
                      background_color="black")]
        ]
        window = Psg.Window("Macro Keyboard Hub", layout, use_default_focus=False, finalize=True, modal=True,
                            no_titlebar=True, auto_close=True, auto_close_duration=1, background_color="black",
                            element_padding=20, keep_on_top=True)
        screen_width, screen_height = GetMonitorInfo(MonitorFromPoint((0, 0))).get("Work")[2:4]
        win_width, win_height = window.size
        x, y = screen_width - win_width - POPUP_PADDING, screen_height - win_height - POPUP_PADDING
        window.move(x, y)
        window.read()

    def __save_configurations(self) -> None:
        """Writes the current configurations in the configuration file
        """
        config_dict = {}
        for config in self.configurations:
            config_dict[config.name] = config.keys
        with open(DEFAULT_FILE_NAME, "w") as file:
            json.dump(config_dict, file)

    @staticmethod
    def __exists_valid_config() -> bool:
        """If the configuration file already exists
        :return: bool if the configuration file exists
        """
        if not os.path.isfile(DEFAULT_FILE_NAME):
            return False
        return True

    @staticmethod
    def __init_config() -> None:
        """Initializes the configuration file, done if it does not exist on startup
        """
        lines = {'default': DEFAULT_CONFIG_KEYS}
        with open(DEFAULT_FILE_NAME, "w") as file:
            json.dump(lines, file)
