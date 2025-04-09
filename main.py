#build line
#pyinstaller --onefile --noconsole --icon=icon.ico --name=CopyPaster --version-file=versioninfo.txt --hidden-import=win10toast --collect-all win10toast main.py

import keyboard
import threading
import time
import pyperclip
import os
from paste import paste_text
from config import TEMP_FOLDER
from capture import capture_and_extract_text
from tray import start_tray_thread, shared_data, update_menu
from utils import (
    focus_last_active_window,
    track_active_window,
    is_target_process_running,
    has_already_restarted,
    clear_restart_flag,
    restart_program,
    seen_pids
)

CHECK_INTERVAL = 2  # seconds

start_tray_thread()
threading.Thread(target=track_active_window, daemon=True).start()

# Hotkeys
keyboard.add_hotkey("ctrl+alt+v", paste_text)
keyboard.add_hotkey("ctrl+alt+c", capture_and_extract_text) 



def on_paste(icon, item):
    print("🔁 Refocusing and pasting...")
    focus_last_active_window()
    paste_text()

print("🔥 Running - Use Ctrl+Alt+C to Copy | Ctrl+Alt+V to Paste")

if __name__ == "__main__":
    # Load seen_pids from the temporary file if it exists
    seen_pids_file = os.path.join(TEMP_FOLDER, "seen_pids.tmp")
    if os.path.exists(seen_pids_file):
        with open(seen_pids_file, "r") as f:
            seen_pids.update(map(int, f.read().split(",")))
        os.remove(seen_pids_file)  # Clean up the temporary file
        print(f"DEBUG: Loaded seen_pids from {seen_pids_file}: {seen_pids}")

    # Add the current process's PID to seen_pids
    seen_pids.add(os.getpid())
    print(f"DEBUG: Added current PID to seen_pids: {seen_pids}")

    # Clear the restart flag at startup
    if has_already_restarted():
        print("DEBUG: Clearing restart flag at startup.")
        clear_restart_flag()
    while True:
        
        old_copied_text = pyperclip.paste() or ""
        if old_copied_text != shared_data["copied_text"]:
            shared_data["copied_text"] = old_copied_text
            update_menu()
            print(f"DEBUG: Menu copied text updated: {shared_data["copied_text"]:}")


        copied_text = pyperclip.paste()
        time.sleep(CHECK_INTERVAL)
        is_running, has_new_instance = is_target_process_running()
        restarted = has_already_restarted()  # Dynamically check the restart flag

        print(f"DEBUG: is_running={is_running}, has_new_instance={has_new_instance}, restarted={restarted}")

        if is_running and has_new_instance:
            if not restarted:
                print("DEBUG: Restarting program due to new instance.")
                restart_program()
            else:
                print("DEBUG: Restart skipped because restarted=True")
        elif not is_running:
            print("DEBUG: No instances running. Clearing restart flag.")
            clear_restart_flag()


