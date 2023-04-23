import json
import os
import PySimpleGUI as Psg
from typing import Dict

from constants import DEFAULT_FILE_NAME, DEFAULT_CONFIG_KEYS


class Configuration:
    def __init__(self, name: str, key_dict: Dict) -> None:
        self.name = name
        self.keys = key_dict


class ConfigurationManager:

    def __init__(self):
        self.configurations = []
        self.configuration_index = 0
        if self.__exists_valid_config():
            self.read_configuration()
        else:
            self.__init_config()

    def read_configuration(self):
        self.configurations.clear()
        with open(DEFAULT_FILE_NAME, "r") as file:
            configs: Dict = json.load(file)
            for name in configs.keys():
                self.configurations.append(
                    Configuration(name=name, key_dict=configs[name])
                )

    def add_new_configuration(self, name: str):
        self.configurations.append(
             Configuration(name=name, key_dict=DEFAULT_CONFIG_KEYS)
        )
        self.configuration_index = len(self.configurations) - 1
        self.__save_configurations()

    def delete_current_configuration(self):
        if len(self.configurations) > 1:
            self.configurations.pop(self.configuration_index)
            self.configuration_index = (self.configuration_index - 1) % len(self.configurations)
            self.__save_configurations()

    def get_key_function(self, key):
        return self.configurations[self.configuration_index].keys[key]

    def update_key(self, key: str, arg: str):
        self.configurations[self.configuration_index].keys[key] = arg
        self.__save_configurations()

    def reset_current_config(self):
        self.configurations[self.configuration_index].keys = DEFAULT_CONFIG_KEYS
        self.__save_configurations()

    def get_configuration(self) -> Configuration:
        return self.configurations[self.configuration_index]

    def next_configuration(self, popup=True):
        if len(self.configurations) > 1:
            self.configuration_index = (self.configuration_index + 1) % len(self.configurations)
            if popup:
                self.__show_configuration_popup()

    def previous_configuration(self, popup=True):
        if len(self.configurations) > 1:
            self.configuration_index = (self.configuration_index - 1) % len(self.configurations)
            if popup:
                self.__show_configuration_popup()

    def __show_configuration_popup(self, blocking=True):
        Psg.popup_auto_close(
            f"Configuration changed to {self.configurations[self.configuration_index].name}",
            keep_on_top=True, relative_location=(0, -800), no_titlebar=True,
            button_type=Psg.POPUP_BUTTONS_NO_BUTTONS, auto_close_duration=1, non_blocking=not blocking)

    @staticmethod
    def __exists_valid_config() -> bool:
        if not os.path.isfile(DEFAULT_FILE_NAME):
            return False
        return True

    def __save_configurations(self):
        config_dict = {}
        for config in self.configurations:
            config_dict[config.name] = config.keys
        with open(DEFAULT_FILE_NAME, "w") as file:
            json.dump(config_dict, file)

    @staticmethod
    def __init_config() -> None:
        lines = {'default': DEFAULT_CONFIG_KEYS}
        with open(DEFAULT_FILE_NAME, "w") as file:
            json.dump(lines, file)

ConfigurationManager()