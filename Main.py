import tkinter
from tkinter.colorchooser import askcolor
import customtkinter
import threading
import time
from pynput import keyboard
import json
import os
import subprocess

# Config
NUM_CLICK_POSITIONS = 20
DEFAULT_ACCENT_COLOR = "#1F6AA5"
CONFIG_DIR = "multiclicker_configs"
ICON_FILE = "my_icon.ico"
AHK_SCRIPT_NAME = "click_backend.ahk"

AHK_EXECUTABLE_PATH = r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
AHK_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), AHK_SCRIPT_NAME)

class AutoClickerThread(threading.Thread):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.running = False
        self.daemon = True

    def start_clicking(self): self.running = True
    def stop_clicking(self): self.running = False

    def run_ahk_click(self, x, y, clicks):
        if not self.running: return
        cmd = [ AHK_EXECUTABLE_PATH, AHK_SCRIPT_PATH, str(x), str(y), str(clicks) ]
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, check=True, startupinfo=startupinfo)

    def run(self):
        while True: 
            if self.running and self.settings['mode'] == 'Multi':
                loop_count = 0
                while self.running and (self.settings['loop'] or loop_count < 1):
                    for point in self.settings['points']:
                        if not self.running: break
                        if point['enabled']:
                            x, y = point['coords']
                            clicks = point['clicks']
                            self.run_ahk_click(x, y, clicks)
                            time.sleep(self.settings['delay'])
                    if self.settings['loop']: loop_count += 1
                self.running = False
            time.sleep(0.1)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Multi-Clicker")
        self.geometry("600x650")
        customtkinter.set_appearance_mode("Dark")

        try:
            if os.path.exists(ICON_FILE): self.iconbitmap(ICON_FILE)
        except Exception: pass

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        if not os.path.exists(AHK_EXECUTABLE_PATH) or not os.path.exists(AHK_SCRIPT_PATH):
            self._show_dependency_error()
            return

        self.accent_color = DEFAULT_ACCENT_COLOR
        self.accent_widgets = []

        self.always_on_top_var = customtkinter.StringVar(value="off")
        self.click_mode_var = customtkinter.StringVar(value="Multi")
        self.clicker_thread = None

        self._create_top_frame()
        self._create_main_frame()
        self._create_color_config_frame()
        self._create_profile_config_frame()
        self._create_bottom_frame()

        self.on_mode_change()
        self.setup_hotkeys()
        self._setup_config_management()

    def _show_dependency_error(self):
        is_exe_found = os.path.exists(AHK_EXECUTABLE_PATH)
        is_script_found = os.path.exists(AHK_SCRIPT_PATH)
        error_text = (f"ERROR: AutoHotkey dependency not found!\n\n"
                      f"Executable Found: {'Yes' if is_exe_found else 'No'}\n"
                      f"Path Checked: {AHK_EXECUTABLE_PATH}\n\n"
                      f"'{AHK_SCRIPT_NAME}' Found: {'Yes' if is_script_found else 'No'}\n"
                      f"Path Checked: {AHK_SCRIPT_PATH}\n\n"
                      "Please ensure the path in the script is correct and the .ahk file is in the same folder.")
        error_label = customtkinter.CTkLabel(self, text=error_text, text_color="red", font=("Calibri", 16), justify="left")
        error_label.pack(expand=True, padx=20, pady=20)

    def _create_top_frame(self):
        top_frame = customtkinter.CTkFrame(self, corner_radius=0)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=0)
        customtkinter.CTkLabel(top_frame, text="Settings:").grid(row=0, column=0, padx=10, pady=10)
        self.multi_radio = customtkinter.CTkRadioButton(top_frame, text="Multi", variable=self.click_mode_var, value="Multi", command=self.on_mode_change)
        self.always_on_top_check = customtkinter.CTkCheckBox(top_frame, text="Always On Top", command=self.toggle_always_on_top, variable=self.always_on_top_var, onvalue="on", offvalue="off")
        self.accent_widgets.extend([self.multi_radio, self.always_on_top_check])
        self.multi_radio.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.always_on_top_check.grid(row=0, column=3, padx=10, pady=10, sticky="e")

    def _create_main_frame(self):
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)

    def _create_color_config_frame(self):
        color_frame = customtkinter.CTkFrame(self)
        color_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 5))
        customtkinter.CTkLabel(color_frame, text="Accent Color:").pack(side="left", padx=10, pady=5)
        color_button = customtkinter.CTkButton(color_frame, text="Change Color", command=self._open_color_chooser)
        color_button.pack(side="left", padx=10, pady=5)
        self.accent_widgets.append(color_button)

    def _create_profile_config_frame(self):
        profile_frame = customtkinter.CTkFrame(self)
        profile_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        profile_frame.grid_columnconfigure((0, 1, 2), weight=1)
        customtkinter.CTkLabel(profile_frame, text="Configuration Profile:").grid(row=0, column=0, columnspan=3, padx=5, pady=(5,0), sticky="w")
        self.config_combobox = customtkinter.CTkComboBox(profile_frame, values=[])
        self.accent_widgets.append(self.config_combobox)
        self.config_combobox.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        load_button = customtkinter.CTkButton(profile_frame, text="Load", command=self._load_config)
        save_button = customtkinter.CTkButton(profile_frame, text="Save", command=self._save_config)
        delete_button = customtkinter.CTkButton(profile_frame, text="Delete", command=self._delete_config, fg_color="firebrick")
        self.accent_widgets.extend([load_button, save_button])
        load_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        save_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        delete_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

    def _create_bottom_frame(self):
        bottom_frame = customtkinter.CTkFrame(self, corner_radius=0)
        bottom_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        bottom_frame.grid_columnconfigure((0, 1), weight=1)
        self.start_button = customtkinter.CTkButton(bottom_frame, text="Start (F6)", command=self.start_clicking)
        self.stop_button = customtkinter.CTkButton(bottom_frame, text="Stop (F7)", command=self.stop_clicking, state="disabled", fg_color="firebrick")
        self.accent_widgets.append(self.start_button)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def on_mode_change(self, *args):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        if self.click_mode_var.get() == "Single": self._build_single_clicker_ui()
        else: self._build_multi_clicker_ui()
        self._update_widget_colors()

    def _build_single_clicker_ui(self):
        customtkinter.CTkLabel(self.main_frame, text="Single Mode is currently disabled.").pack(padx=20, pady=20)

    def _build_multi_clicker_ui(self):
        config_frame = customtkinter.CTkFrame(self.main_frame)
        config_frame.pack(fill='x', padx=5, pady=5)
        customtkinter.CTkLabel(config_frame, text="Delay Between Click(s):").pack(side='left', padx=5, pady=5)
        self.multi_delay_entry = customtkinter.CTkEntry(config_frame, placeholder_text="e.g., 0.1", width=100)
        self.multi_delay_entry.insert(0, "0.1")
        self.multi_delay_entry.pack(side='left', padx=5, pady=5)
        self.loop_var = customtkinter.IntVar(value=1)
        self.loop_checkbox = customtkinter.CTkCheckBox(config_frame, text="Loop", variable=self.loop_var)
        self.accent_widgets.append(self.loop_checkbox)
        self.loop_checkbox.pack(side='left', padx=10, pady=5)

        self.points_frame = customtkinter.CTkScrollableFrame(self.main_frame, label_text="Click Sequence")
        self.accent_widgets.append(self.points_frame)
        self.points_frame.pack(fill='both', expand=True, padx=5, pady=5)

        headers = ["#", "On", "Name", "Set Position", "Coordinates", "Clicks"]
        self.points_frame.grid_columnconfigure((2, 4), weight=1)
        for col, header in enumerate(headers): 
            customtkinter.CTkLabel(self.points_frame, text=header, font=customtkinter.CTkFont(weight="bold")).grid(row=0, column=col, padx=5, pady=5)

        self.points_ui = []
        import pyautogui
        for i in range(NUM_CLICK_POSITIONS):
            row_num = i + 1
            on_var = customtkinter.IntVar(value=1 if i < 3 else 0)
            checkbox = customtkinter.CTkCheckBox(self.points_frame, text="", variable=on_var)

            name_entry = customtkinter.CTkEntry(self.points_frame, placeholder_text=f"Action #{row_num}")

            get_pos_button = customtkinter.CTkButton(self.points_frame, text="Get Pos", width=80, command=lambda r=i, pg=pyautogui: self.get_mouse_position(r, pg))
            self.accent_widgets.extend([checkbox, get_pos_button])

            customtkinter.CTkLabel(self.points_frame, text=f"#{row_num}").grid(row=row_num, column=0, padx=5)
            checkbox.grid(row=row_num, column=1, padx=5)
            name_entry.grid(row=row_num, column=2, padx=5, pady=2, sticky="ew")
            get_pos_button.grid(row=row_num, column=3, padx=5, pady=2)
            pos_label = customtkinter.CTkLabel(self.points_frame, text="Not Set", anchor="w")
            pos_label.grid(row=row_num, column=4, padx=10, sticky="ew")
            clicks_entry = customtkinter.CTkEntry(self.points_frame, width=50)
            clicks_entry.insert(0, "1")
            clicks_entry.grid(row=row_num, column=5, padx=5)

            self.points_ui.append({'on_var': on_var, 'name_entry': name_entry, 'pos_label': pos_label, 'clicks_entry': clicks_entry, 'coords': None})

    def _open_color_chooser(self):
        picked_color = askcolor(title="Choose Accent Color")
        if picked_color and picked_color[1]:
            self.accent_color = picked_color[1]
            self._update_widget_colors()

    def _update_widget_colors(self):
        for widget in self.accent_widgets:
            if isinstance(widget, customtkinter.CTkComboBox):
                widget.configure(button_color=self.accent_color)
            elif isinstance(widget, customtkinter.CTkScrollableFrame):
                widget.configure(scrollbar_button_color=self.accent_color)
            else:
                widget.configure(fg_color=self.accent_color)

    def get_mouse_position(self, row_index, pg_module):
        label = self.points_ui[row_index]['pos_label']
        label.configure(text="Getting pos in 3s...")
        self.after(1000, lambda: label.configure(text="Getting pos in 2s..."))
        self.after(2000, lambda: label.configure(text="Getting pos in 1s..."))
        self.after(3000, lambda r=row_index, pg=pg_module: self._capture_position(r, pg))
    def _capture_position(self, row_index, pg_module):
        pos = pg_module.position()
        self.points_ui[row_index]['coords'] = (pos.x, pos.y)
        self.points_ui[row_index]['pos_label'].configure(text=f"({pos.x}, {pos.y})")

    def start_clicking(self):
        if self.start_button.cget("state") == "disabled": return
        settings = {'mode': self.click_mode_var.get()}
        try:
            settings['delay'] = float(self.multi_delay_entry.get())
            settings['loop'] = self.loop_var.get() == 1
            settings['points'] = []
            for i, point_ui in enumerate(self.points_ui):
                if point_ui['on_var'].get() == 1:
                    if point_ui['coords'] is None:
                        tkinter.messagebox.showerror("Error", f"Position for point #{i+1} is not set.")
                        return
                    settings['points'].append({'enabled': True, 'coords': point_ui['coords'], 'clicks': int(point_ui['clicks_entry'].get())})
            if not settings['points']:
                    tkinter.messagebox.showwarning("Warning", "No points were enabled in the sequence.")
                    return
        except (ValueError, AttributeError):
            tkinter.messagebox.showerror("Error", "Invalid input. Please ensure delays and click counts are numbers.")
            return
        self.clicker_thread = AutoClickerThread(settings)
        self.clicker_thread.start()
        self.clicker_thread.start_clicking()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        if not settings['loop']: self.after(50, self.check_if_thread_is_done)

    def check_if_thread_is_done(self):
        if self.clicker_thread and not self.clicker_thread.is_alive(): self.stop_clicking()
        else: self.after(100, self.check_if_thread_is_done)

    def stop_clicking(self):
        if self.clicker_thread: self.clicker_thread.stop_clicking()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def _setup_config_management(self):
        if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR)
        self._refresh_config_list()
    def _refresh_config_list(self):
        try:
            configs = sorted([f.replace(".json", "") for f in os.listdir(CONFIG_DIR) if f.endswith(".json")])
            self.config_combobox.configure(values=configs)
            self.config_combobox.set(configs[0] if configs else "")
        except Exception as e: print(f"Config refresh error: {e}")

    def _save_config(self):
        dialog = customtkinter.CTkInputDialog(text="Enter a name for this configuration:", title="Save Configuration")
        name = dialog.get_input()
        if not name or not name.strip(): return

        config_data = {
            "mode": "Multi", "delay": self.multi_delay_entry.get(),
            "loop": self.loop_var.get(), "accent_color": self.accent_color,
            "points": []
        }

        for point_ui in self.points_ui:
            config_data["points"].append({
                "enabled": point_ui["on_var"].get(),
                "name": point_ui["name_entry"].get(),
                "coords": point_ui["coords"],
                "clicks": point_ui["clicks_entry"].get()
            })
        try:
            with open(os.path.join(CONFIG_DIR, f"{name.strip()}.json"), 'w') as f: json.dump(config_data, f, indent=4)
            self._refresh_config_list()
            self.config_combobox.set(name.strip())
        except Exception as e: tkinter.messagebox.showerror("Save Error", f"Failed to save configuration: {e}")

    def _load_config(self):
        name = self.config_combobox.get()
        if not name: return tkinter.messagebox.showwarning("Load Warning", "No configuration selected.")
        try:
            with open(os.path.join(CONFIG_DIR, f"{name}.json"), 'r') as f: config_data = json.load(f)
            self.click_mode_var.set(config_data.get("mode", "Multi"))
            self.on_mode_change()
            self.after(10, lambda: self._apply_config_data(config_data))
        except Exception as e: tkinter.messagebox.showerror("Load Error", f"Failed to load configuration: {e}")

    def _apply_config_data(self, config_data):
        """MODIFIED: Applies all data from a loaded config, including the new name field."""
        try:
            self.accent_color = config_data.get("accent_color", DEFAULT_ACCENT_COLOR)
            self._update_widget_colors()

            self.multi_delay_entry.delete(0, 'end'); self.multi_delay_entry.insert(0, config_data.get("delay", "0.1"))
            self.loop_var.set(config_data.get("loop", 1))
            for i, point_data in enumerate(config_data.get("points", [])):
                if i < len(self.points_ui):
                    self.points_ui[i]["on_var"].set(point_data.get("enabled", 0))
                    self.points_ui[i]["clicks_entry"].delete(0, 'end'); self.points_ui[i]["clicks_entry"].insert(0, point_data.get("clicks", "1"))

                    self.points_ui[i]["name_entry"].delete(0, 'end')
                    self.points_ui[i]["name_entry"].insert(0, point_data.get("name", ""))

                    coords = point_data.get("coords"); self.points_ui[i]["coords"] = coords
                    self.points_ui[i]["pos_label"].configure(text=f"({coords[0]}, {coords[1]})" if coords else "Not Set")
        except Exception as e: tkinter.messagebox.showerror("Apply Config Error", f"An error occurred applying settings: {e}")

    def _delete_config(self):
        name = self.config_combobox.get()
        if not name: return tkinter.messagebox.showwarning("Delete Warning", "No configuration selected.")
        if not tkinter.messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{name}'?"): return
        try:
            os.remove(os.path.join(CONFIG_DIR, f"{name}.json"))
            self._refresh_config_list()
        except Exception as e: tkinter.messagebox.showerror("Delete Error", f"Failed to delete configuration: {e}")

    def toggle_always_on_top(self):
        self.attributes("-topmost", self.always_on_top_var.get() == 'on')

    def setup_hotkeys(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f6 and self.start_button.cget("state") == "normal": self.after(0, self.start_clicking)
                elif key == keyboard.Key.f7 and self.stop_button.cget("state") == "normal": self.after(0, self.stop_clicking)
            except AttributeError: pass
        listener = keyboard.Listener(on_press=on_press); listener.daemon = True; listener.start()

if __name__ == "__main__":
    try:
        import pyautogui
    except ImportError:
        print("PyAutoGUI not found. Please install it: pip install pyautogui")
        exit()
    
    app = App()
    app.mainloop()