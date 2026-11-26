# Endless Macro

Modern, lightweight, and open-source mouse and keyboard macro utility for Windows.
Built with Python + customtkinter + pynput. Licensed under the MIT License.

## Features

* **Mouse**, **Keyboard**, and **Mouse + Keyboard** modes
* Mouse: left click, right click, middle click. Spam or Hold. No speed limits.
* Keyboard: 5 slots, empty slots are skipped, Spam / Hold, interval in seconds.
* **Sequence:** keyboard slots run in order rather than simultaneously.
* Selectable trigger key and two working modes:
* **Auto:** press the key once to start, press again to stop.
* **Manual:** runs while holding the key down, stops when released.


* Start delay, auto-stop, always on top
* In-app guide (? buttons and Guide)
* Settings are saved automatically (`%APPDATA%\EndlessMacro`)

## Creating a Standalone Executable (.exe)

1. Install Python 3.12 or 3.13 (make sure to check the **Add python.exe to PATH** box during installation).
2. Double-click the `build.bat` file in this folder.
3. Once finished, `dist\EndlessMacro.exe` will be generated. It works even on computers without Python installed, you just need to share the single executable file.

## Running from Source

```
pip install -r requirements.txt
python endless_macro.py

```

## Notes

* There are no speed limits, but actual speed depends on your computer and open programs. Extremely high values may slow down the system. The stop key always works.
* If the program you are using the macro in runs as administrator, run Endless Macro as administrator as well.
* Some games' anti-cheat systems may block macro programs. Usage responsibility belongs to you.
* Some antivirus software may trigger false positive warnings for programs listening to mouse and keyboard input.