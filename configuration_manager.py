import json
import os
import PySimpleGUI as Psg
from typing import Dict

from constants import DEFAULT_FILE_NAME, DEFAULT_CONFIG_KEYS


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
        Psg.popup_auto_close(
            f"Configuration changed to {self.configurations[self.configuration_index].name}",
            keep_on_top=True, relative_location=(0, -800), no_titlebar=True,
            button_type=Psg.POPUP_BUTTONS_NO_BUTTONS, auto_close_duration=1
        )

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


ConfigurationManager()
