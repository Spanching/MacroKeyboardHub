from dotenv import load_dotenv
import logging

from macro_keyboard_configuration_management.constants import LOGGING_FILE_NAME
from macro_keyboard_listener.listener import MacroKeyboard

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(levelname)s:%(message)s', filemode='w', filename=LOGGING_FILE_NAME,
                        encoding='utf-8', level=logging.INFO)
    load_dotenv()
    MacroKeyboard()
