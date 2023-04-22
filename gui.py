import PySimpleGUI as sg
import keyboard
import os
from pathlib import Path

class GUI:
    def __init__(self) -> None:
        sg.theme("Dark Grey 15")
        self.key_dict = {}

        self.files = list(filter(lambda f: f.endswith(".mkc"), os.listdir()))
        self.file_index = 0

        self.read_config()
        button_lists = [[], [], [], []]
        for index, (key, value) in enumerate(self.key_dict.items()):
            button_lists[index // 4].append(sg.Button(value, key = f"BUTTON_{key}", size=(12, 5)))
        layout = [
            [sg.Button("<", key="PREV"), sg.Text(self.files[self.file_index], key="-TEXT-CONFIG-", expand_x=True, justification="center"), sg.Button(">", key="NEXT"), sg.Button("+", key="ADD_CONFIG"), sg.Button("Delete", key="DELETE_CONFIG")],
            *button_lists
        ]
        self.window = sg.Window("Macro Keyboard Hub", layout)

    def read_config(self):
        self.key_dict.clear()
        with open(self.files[self.file_index], "r") as file:
            lines = file.readlines()
            for line in lines:
                key, arg = line.strip().split(',')
                self.key_dict[key] = arg

    def update_buttons(self):
        for key, arg in self.key_dict.items():
            self.window[f"BUTTON_{key}"](arg)

    def record(self) -> str:
        pressed = 0
        key_list=[]
        self.recording = True
        while True:
            event = keyboard.read_event()
            if event.event_type == "down":
                key_list.append(event.name)
                pressed = pressed + 1
            elif event.event_type == "up":
                pressed = pressed - 1
            if pressed == 0:
                arg = '+'.join(key_list)
                return arg
            
    def record_macro(self, window, key):
        input = self.record()
        window[f"BUTTON_{key}"](input)
        self.key_dict[key] = input
    
    def save_config(self):
        lines = list(map(lambda pair: f"{pair[0]},{pair[1]}\n" ,self.key_dict.items()))
        with open(self.files[self.file_index], "w") as file:
            file.writelines(lines)

    def show_gui(self):
        # Create an event loop
        while True:
            event, _ = self.window.read()
            if event is not None:
                if event == "ADD_CONFIG":
                    config_name = sg.popup_get_text("Input the name of the new configuration.")
                    if config_name is not None:
                        Path(f'{config_name}.mkc').touch()
                        lines = ['f13,f13\n',
                                'f14,f14\n',
                                'f15,f15\n',
                                'f16,f16\n',
                                'f17,f17\n',
                                'f18,f18\n',
                                'f19,f19\n',
                                'f20,f20\n',
                                'strg+f13,strg+f13\n',
                                'strg+f14,strg+f14\n',
                                'strg+f15,strg+f15\n',
                                'strg+f16,strg+f16\n',
                                'strg+f17,strg+f17\n',
                                'strg+f18,strg+f18\n',
                                'strg+f19,strg+f19\n',
                                'strg+f20,strg+f20\n',
                            ]
                        with open(f'{config_name}.mkc', "w") as file: 
                                    file.writelines(lines)
                        self.files = list(filter(lambda f: f.endswith(".mkc"), os.listdir()))
                elif event == "DELETE_CONFIG":
                    if len(self.files) > 1:
                        os.remove(self.files[self.file_index])
                        self.files = list(filter(lambda f: f.endswith(".mkc"), os.listdir()))
                        self.file_index = self.file_index % len(self.files)
                        self.window["-TEXT-CONFIG-"](self.files[self.file_index])
                        self.read_config()
                        self.update_buttons()
                elif event == "PREV":
                    self.file_index = (self.file_index - 1) % len(self.files)
                    self.window["-TEXT-CONFIG-"](self.files[self.file_index])
                    self.read_config()
                    self.update_buttons()
                elif event == "NEXT":
                    self.file_index = (self.file_index + 1) % len(self.files)
                    self.window["-TEXT-CONFIG-"](self.files[self.file_index])
                    self.read_config()
                    self.update_buttons()
                elif event.startswith("BUTTON_"):
                    key = event.split("_")[-1]
                    self.record_macro(self.window, key)
                    self.save_config()
            if event == sg.WIN_CLOSED:
                break

        self.window.close()

GUI().show_gui()

