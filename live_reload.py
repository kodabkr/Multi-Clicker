import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SCRIPT_TO_RUN = "Main.py"

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            print("Change detected -> Restarting")
            self.process.terminate()
            self.process.wait()

        self.process = subprocess.Popen(["python", SCRIPT_TO_RUN])

    def on_modified(self, event):
        if event.src_path.endswith(SCRIPT_TO_RUN): # type: ignore
            self.start_process()

if __name__ == "__main__":
    if not os.path.exists(SCRIPT_TO_RUN):
        print(f"Error: The script '{SCRIPT_TO_RUN}' was not found.")
        exit()

    print("Starting Live Reload")
    print(f"Watching '{SCRIPT_TO_RUN}' for changes...")

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
            event_handler.process.wait()

    observer.join()
    print("Reloader Stopped")