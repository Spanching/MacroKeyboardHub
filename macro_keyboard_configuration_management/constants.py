"""
This file contains constant values for this project, mostly string values and the default configuration mapping for
the MacroKeyboard
"""

MACRO_KEYBOARD_FILE_TYPE = ".mkc"
LOGGING_FILE_NAME = "macrokeyboardhub.log"

ABBREVIATION = "ABBR"
BUTTON = "BUTTON"
INTERNAL_FUNCTION = "FKT"
NEXT = "NEXT"
PREV = "PREV"
DELETE = "DELETE"
ADD = "ADD"
RESET = "RESET"
CONFIG = "CONFIG"
CANCEL = "CANCEL"
EDIT = "EDIT"

DEFAULT_FILE_NAME = "configuration.mkc"
DEFAULT_CONFIG_KEYS = {
    'f13': {"name": None, 'arg': 'f13', 'function_type': 'MACRO'},
    'f14': {"name": None, 'arg': 'f14', 'function_type': 'MACRO'},
    'f15': {"name": None, 'arg': 'f15', 'function_type': 'MACRO'},
    'f16': {"name": None, 'arg': 'f16', 'function_type': 'MACRO'},
    'f17': {"name": None, 'arg': 'f17', 'function_type': 'MACRO'},
    'f18': {"name": None, 'arg': 'f18', 'function_type': 'MACRO'},
    'f19': {"name": None, 'arg': 'f19', 'function_type': 'MACRO'},
    'f20': {"name": None, 'arg': 'f20', 'function_type': 'MACRO'},
    'strg+f13': {"name": None, 'arg': 'strg+f13', 'function_type': 'MACRO'},
    'strg+f14': {"name": None, 'arg': 'strg+f14', 'function_type': 'MACRO'},
    'strg+f15': {"name": None, 'arg': 'strg+f15', 'function_type': 'MACRO'},
    'strg+f16': {"name": None, 'arg': 'strg+f16', 'function_type': 'MACRO'},
    'strg+f17': {"name": None, 'arg': 'strg+f17', 'function_type': 'MACRO'},
    'strg+f18': {"name": None, 'arg': 'strg+f18', 'function_type': 'MACRO'},
    'strg+f19': {"name": None, 'arg': 'FKT_PREV', 'function_type': 'MACRO'},
    'strg+f20': {"name": None, 'arg': 'FKT_NEXT', 'function_type': 'MACRO'},
}

POPUP_PADDING = 20
