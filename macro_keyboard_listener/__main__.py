import logging

from dotenv import load_dotenv
import os

from macro_keyboard_configuration_management.constants import LOGGING_FILE_NAME
from macro_keyboard_listener.listener import MacroKeyboard


def __init_env() -> None:
    """Initializes the .env file if it does not exist
    """
    if not os.path.isfile(".env"):
        with open(".env", 'w') as env_file:
            env_file.writelines([
                'USE_FOREGROUND_WINDOW_DETECTION = True\n',
                'EXE_LIST = ["chrome.exe", "explorer.exe"]\n'
            ])


if __name__ == "__main__":
    __init_env()
    load_dotenv()
    logging.basicConfig(format='%(asctime)s  %(levelname)s:%(message)s', filemode='w', filename=LOGGING_FILE_NAME,
                        encoding='utf-8', level=logging.INFO)
    logging.info("Environment file loaded")
    try:
        MacroKeyboard()
    except Exception as e:
        logging.warning(e)
