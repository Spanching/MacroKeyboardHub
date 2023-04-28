import json
import os
from enum import Enum
from typing import Dict, List

from macro_keyboard_configuration_management.constants import DEFAULT_FILE_NAME, DEFAULT_CONFIG_KEYS
import logging


class FunctionType(str, Enum):
    """The type of the Function for a key
    """
    MACRO = "MACRO"
    INTERNAL = "INTERNAL"
    ABBREVIATION = "ABBREVIATION"


class KeyFunction:
    """Represents the Function of a Key
    """

    def __init__(self, arg: str, function_type=FunctionType.MACRO, name: str = None) -> None:
        self.arg = arg
        self.function_type = function_type
        self.name = name

    def get_name(self) -> str:
        """Returns the displayable name for the KeyFunction
        :return: str, the string representation for the KeyFunction
        """
        if self.function_type == FunctionType.ABBREVIATION:
            return self.name
        return self.arg.replace('+', ' + ')

    def to_dict(self) -> Dict:
        """Maps KeyFunction to dictionary
        :return: Dict representing this KeyFunction
        """
        return {
            "name": self.name,
            "arg": self.arg,
            "function_type": self.function_type.name
        }


class Configuration:
    def __init__(self, name: str, keys: Dict[str, KeyFunction]) -> None:
        """Represents a configuration for the MacroKeyboard
        :param name: the name of this representation
        :param keys: the mapping of keys to their function
        """
        self.name = name
        self.keys = keys


class ConfigurationManager:

    def __init__(self):
        """Handles persistence of Configurations and changes, used by GUI and Listener without synchronization of
        indices, but with synchronized configurations
        """
        self.locked_configuration = False
        self.configurations: List[Configuration] = []
        self.configuration_index = 0
        self.__update_config()
        logging.info("Configuration Manager initialized")

    def toggle_configuration_lock(self) -> None:
        """Toggles configuration lock
        """
        self.locked_configuration = not self.locked_configuration

    def set_configuration_for_process(self, process: str) -> bool:
        """Sets configuration when foreground executable changes
        :param process: the name of the process that is now in the foreground
        """
        if self.locked_configuration:
            logging.info(f"No configuration set for process {process} as configuration is locked")
            return False
        for index, config in enumerate(self.configurations):
            if config.name == process:
                if self.configuration_index != index:
                    self.configuration_index = index
                    logging.info(f"Set configuration for process {process}")
                    return True
        logging.info(f"No configuration set for process {process}")
        return False

    def read_configuration(self) -> None:
        """Reads the configuration file and updates the configurations list
        """
        self.configurations.clear()
        with open(DEFAULT_FILE_NAME, "r") as file:
            configs: Dict = json.load(file)
            for configuration_name in configs.keys():
                key_dict = {}
                config = configs[configuration_name]
                for key in config.keys():
                    name, arg, function_type = config[key].values()
                    key_dict[key] = KeyFunction(arg, FunctionType(function_type), name)
                self.configurations.append(
                    Configuration(name=configuration_name, keys=key_dict)
                )

    def get_configuration(self) -> Configuration:
        """Returns the currently active configuration for this instance
        :return: Configuration that is currently active
        """
        return self.configurations[self.configuration_index]

    def next_configuration(self) -> None:
        """Increments the index for the configurations
        """
        if len(self.configurations) > 1:
            self.configuration_index = (self.configuration_index + 1) % len(self.configurations)
            logging.info(f"Switching to next configuration at index {self.configuration_index} "
                         f"with name {self.configurations[self.configuration_index].name}")

    def previous_configuration(self) -> None:
        """Decrements the index for the configurations
        """
        if len(self.configurations) > 1:
            self.configuration_index = (self.configuration_index - 1) % len(self.configurations)
            logging.info(f"Switching to previous configuration at index {self.configuration_index} "
                         f"with name {self.configurations[self.configuration_index].name}")

    # GUI Functions
    def add_new_configuration(self, name: str) -> None:
        """Adds a new configuration with the default function mapping
        :param name: the name for the new configuration
        """
        self.configurations.append(
            Configuration(name=name, keys=self.configurations[self.configuration_index].keys)
        )
        self.configuration_index = len(self.configurations) - 1
        self.__save_configurations()
        logging.info(f"Adding configuration {name}")

    def delete_current_configuration(self) -> None:
        """Deletes the currently active Configuration
        """
        if len(self.configurations) > 1:
            deleted = self.configurations.pop(self.configuration_index)
            self.configuration_index = (self.configuration_index - 1) % len(self.configurations)
            self.__save_configurations()
            logging.info(f"Deleted configuration {deleted.name}")

    def get_key_function(self, key: str) -> KeyFunction:
        """Returns the function for a key
        :param key: the key we want the function for
        :return: string representation of the key function
        """
        return self.configurations[self.configuration_index].keys[key]

    def update_key(self, key: str, function: KeyFunction) -> None:
        """Updates the function for a given key
        :param key: the key to update the function for
        :param function: The KeyFunction to update the key to
        """
        logging.info(f"Updating key {key}: {function.get_name()}")
        self.configurations[self.configuration_index].keys[key] = function
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
            key_dict = {}
            key: str
            function: KeyFunction
            for key, function in config.keys.items():
                key_dict[key] = function.to_dict()
            config_dict[config.name] = key_dict
        with open(DEFAULT_FILE_NAME, "w") as file:
            json.dump(config_dict, file)

    def __update_config(self) -> None:
        """Save default configuration if configuration file does not exist already and
        loads configuration from file
        """
        if not os.path.isfile(DEFAULT_FILE_NAME):
            lines = {'default': DEFAULT_CONFIG_KEYS}
            with open(DEFAULT_FILE_NAME, "w") as file:
                json.dump(lines, file)
            logging.info("Wrote default config file")
        self.configurations.clear()
        self.read_configuration()
        logging.info("Configuration loaded from file")
