import logging
from macro_keyboard_hub.gui import GUI

from macro_keyboard_configuration_management.constants import LOGGING_FILE_NAME

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(levelname)s:%(message)s', filemode='w', filename='gui.log',
                        encoding='utf-8', level=logging.DEBUG)
    GUI().start()
