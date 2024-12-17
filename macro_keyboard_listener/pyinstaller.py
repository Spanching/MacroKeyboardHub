import PyInstaller.__main__
from pathlib import Path

HERE = Path(__file__).parent.absolute()
path_to_main = str(HERE / "__main__.py")

def install():
    PyInstaller.__main__.run([
        path_to_main,
        "--onefile",
        "-w",
        "-n listener"
        # other pyinstaller options... 
    ])