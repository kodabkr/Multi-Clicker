# 10in1 Multi-Clicker Overview

This document explains the functionality and structure of the `10in1` Multi-Clicker program.

## Purpose

The `10in1` Multi-Clicker is a Windows desktop application that automates mouse clicks at multiple user-defined screen positions. It is designed to streamline repetitive clicking tasks, such as testing, gaming, or productivity workflows, by allowing users to configure and execute complex click sequences with ease.

## Features

1. **Multi-Point Click Sequences:** Configure up to 15 click positions, each with its own coordinates and click count.
2. **Looping:** Optionally repeat the entire click sequence automatically.
3. **Configurable Delay:** Set a custom delay between each click in the sequence.
4. **Profile Management:** Save, load, and delete named configuration profiles for different tasks.
5. **Hotkey Support:** Start and stop clicking using global hotkeys (F6 to start, F7 to stop).
6. **Always On Top:** Option to keep the application window above others.
7. **AutoHotkey Backend:** Uses an AutoHotkey script for reliable and fast mouse automation.
8. **User-Friendly GUI:** Built with CustomTkinter for a modern, dark-themed interface.
9. **Error Handling:** Provides clear error messages for missing dependencies or invalid input.
10. **Portable Configurations:** All settings are stored as JSON files for easy backup and sharing.

## Usage

To use the program, run the following command in the application directory:

```sh
python Main.py
```

**Requirements:**
- Python 3.x
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [pyautogui](https://pypi.org/project/pyautogui/)
- [pynput](https://pypi.org/project/pynput/)
- [AutoHotkey v2](https://www.autohotkey.com/) installed at the path specified in the script

## Example Workflow

1. Launch the application.
2. For each click position, click "Get Pos" and place your mouse where you want to click (wait for the countdown).
3. Set the number of clicks for each position.
4. Adjust the delay and enable looping if needed.
5. Save your configuration for future use.
6. Press **F6** or click "Start" to begin the sequence. Press **F7** or "Stop" to halt.

## Script Structure

- **Main.py:** The main GUI application and logic.
- **click_backend.ahk:** AutoHotkey script called by the Python app to perform mouse clicks.
- **multiclicker_configs/**: Folder where configuration profiles are saved as JSON.
- **my_icon.ico:** (Optional) Application icon.

## Contribution

Feel free to contribute by submitting pull requests or reporting issues.

## License

This project is licensed under the MIT License.
