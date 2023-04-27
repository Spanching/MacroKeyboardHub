import json
import os
from typing import Dict, Callable, List

from dotenv import load_dotenv

from macro_keyboard_configuration_management.constants import DEFAULT_FILE_NAME, DEFAULT_CONFIG_KEYS
import logging


class Configuration:
    def __init__(self, name: str, key_dict: Dict) -> None:
        """Represents a configuration for the MacroKeyboard
        :param name: the name of this representation
        :param key_dict: the mapping of keys to their function
        """
        self.name = name
        self.keys = key_dict


class ConfigurationManager:

    def __init__(self, popup_callback: Callable = None):
        """Handles persistence of Configurations and changes, used by GUI and Listener without synchronization of
        indices, but with synchronized configurations
        """
        self.popup_callback = popup_callback
        self.configurations: List[Configuration] = []
        self.configuration_index = 0
        self.__update_config()
        self.__get_logger().info("Configuration Manager initialized")

    def set_configuration_for_process(self, process: str) -> bool:
        """Sets configuration when foreground executable changes
        :param process: the name of the process that is now in the foreground
        """
        for index, config in enumerate(self.configurations):
            if config.name == process:
                if self.configuration_index != index:
                    self.configuration_index = index
                    if self.popup_callback is not None:
                        self.popup_callback()
                    self.__get_logger().info(f"Set configuration for process {process}")
                    return True
        self.__get_logger().info(f"No configuration set for process {process}")
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
            self.__get_logger().info(f"Switching to next configuration at index {self.configuration_index} "
                                     f"with name {self.configurations[self.configuration_index].name}")
            if popup and self.popup_callback is not None:
                self.popup_callback()

    def previous_configuration(self, popup=True) -> None:
        """Decrements the index for the configurations
        :param popup: if to display a popup (only wanted for changes from the keyboard itself)
        """
        if len(self.configurations) > 1:
            self.configuration_index = (self.configuration_index - 1) % len(self.configurations)
            self.__get_logger().info(f"Switching to previous configuration at index {self.configuration_index} "
                                     f"with name {self.configurations[self.configuration_index].name}")
            if popup and self.popup_callback is not None:
                self.popup_callback()

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
        self.__get_logger().info(f"Adding configuration {name}")

    def delete_current_configuration(self) -> None:
        """Deletes the currently active Configuration
        """
        if len(self.configurations) > 1:
            deleted = self.configurations.pop(self.configuration_index)
            self.configuration_index = (self.configuration_index - 1) % len(self.configurations)
            self.__save_configurations()
            self.__get_logger().info(f"Deleted configuration {deleted.name}")

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
        self.__get_logger().info(f"Updating key {key} with argument {arg}")
        self.configurations[self.configuration_index].keys[key] = arg
        self.__save_configurations()

    def reset_current_config(self) -> None:
        """Resets the currently active configuration to the default function mapping
        """
        self.configurations[self.configuration_index].keys = DEFAULT_CONFIG_KEYS
        self.__save_configurations()

    def __save_configurations(self) -> None:
        """Writes the current configurations in the configuration file
        """
        config_dict = {}
        for config in self.configurations:
            config_dict[config.name] = config.keys
        with open(DEFAULT_FILE_NAME, "w") as file:
            json.dump(config_dict, file)

    def __update_config(self) -> None:
        """Save default config if configuration file does not exist already
        load config from file if it exists
        """
        if not os.path.isfile(DEFAULT_FILE_NAME):
            lines = {'default': DEFAULT_CONFIG_KEYS}
            with open(DEFAULT_FILE_NAME, "w") as file:
                json.dump(lines, file)
            self.__get_logger().info("Wrote default config file")
        self.configurations.clear()
        with open(DEFAULT_FILE_NAME, "r") as file:
            configs: Dict = json.load(file)
            for name in configs.keys():
                self.configurations.append(
                    Configuration(name=name, key_dict=configs[name])
                )
        self.__get_logger().info("Configuration loaded from file")

    @staticmethod
    def __get_logger():
        return logging.getLogger()

