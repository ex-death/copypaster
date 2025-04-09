from PIL import Image
import win32gui
import win32ui
import win32con
import pygetwindow as gw
from pywinauto.application import Application
import time
import os
import sys
import psutil
import subprocess
import atexit
from config import TEMP_FOLDER



last_active_title = None
seen_pids = set()  # Initialize seen_pids as a global variable
seen_pids_file = os.path.join(TEMP_FOLDER, "seen_pids.tmp")

TARGET_PROCESS = "ncplayer.exe"  # Replace with your app

FLAG_FILE = os.path.join(TEMP_FOLDER, "app_restart_flag.tmp")


def is_target_process_running():
    """Check if the target process is running and detect new instances."""
    global seen_pids

    current_pids = set()
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] == TARGET_PROCESS:
            current_pids.add(proc.info['pid'])

    # Exclude the current process's PID
    current_pids.discard(os.getpid())

    # Detect new instances
    new_instances = current_pids - seen_pids
    print(f"DEBUG: current_pids={current_pids}, seen_pids={seen_pids}, new_instances={new_instances}")

    # Update seen_pids
    seen_pids.update(current_pids)
    print(f"DEBUG: Updated seen_pids={seen_pids}")

    return len(current_pids) > 0, len(new_instances) > 0

def has_already_restarted():
    return os.path.exists(FLAG_FILE)

def set_restart_flag():
    with open(FLAG_FILE, 'w') as f:
        f.write("restarted")

def clear_restart_flag():
    if os.path.exists(FLAG_FILE):
        print("DEBUG: Removing FLAG_FILE.")
        os.remove(FLAG_FILE)
    else:
        print("DEBUG: FLAG_FILE does not exist.")

# Register the function to run on exit
atexit.register(clear_restart_flag)

def restart_program():
    global seen_pids
    print("DEBUG: restart_program called.")
    set_restart_flag()

    # Serialize seen_pids to a temporary file
    with open(seen_pids_file, "w") as f:
        f.write(",".join(map(str, seen_pids)))
    print(f"DEBUG: Serialized seen_pids to {seen_pids_file}: {seen_pids}")

    # Hide and stop the tray icon
    from tray import tray_icon  # Import the tray_icon object
    if tray_icon:
        tray_icon.visible = False
        tray_icon.stop()

    # Unregister the atexit handler to prevent clearing the restart flag during restart
    atexit.unregister(clear_restart_flag)

    print("Restarting app...")
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
        executable = sys.executable  # Path to the .exe file
        print(f"DEBUG: Restarting executable: {executable}")
        subprocess.Popen([executable])
    else:
        script_path = os.path.abspath(sys.argv[0]) if sys.argv[0] else __file__
        print(f"DEBUG: Restarting script: {script_path}")
        subprocess.Popen([sys.executable, script_path])
    sys.exit()

# def restart_app():
#     """Restart the application."""
#     print("🔄 Restarting application...")
#     if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
#         # Restart the executable
#         print(f"sys.executable: {sys.executable}")
#         os.execv(sys.executable, [sys.executable] + sys.argv[1:])
#     else:
#         # Restart the script
#         script_path = os.path.abspath(sys.argv[0]) if sys.argv[0] else __file__
#         working_dir = os.path.dirname(script_path)
#         os.chdir(working_dir)  # Ensure the working directory is set to the script's location
#         print(f"sys.argv[0]: {sys.argv[0]}")
#         print(f"Resolved script path: {script_path}")
#         print(f"sys.executable: {sys.executable}")
#         if not os.path.isfile(script_path):
#             print(f"❌ Error: Script file not found: {script_path}")
#             return
#         os.execv(sys.executable, [sys.executable, script_path] + sys.argv[1:])



def screen_grab_win32(bbox):
    left, top, right, bottom = bbox
    width, height = right - left, bottom - top

    hwnd = win32gui.GetDesktopWindow()
    hwindc = win32gui.GetWindowDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    win32gui.DeleteObject(bmp.GetHandle())
    memdc.DeleteDC()
    srcdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)

    return im

def focus_last_active_window():
    try:
        # Get the currently active window BEFORE tray steals focus
        windows = gw.getWindowsWithTitle('')
        # Find first non-minimized, non-system window
        for win in windows:
            if win.isActive and not win.title.startswith("CopyPasta"):
                return win

        # Fallback: focus first found normal window
        for win in windows:
            if win.title:
                app = Application().connect(handle=win._hWnd)
                app_dialog = app.window(handle=win._hWnd)
                app_dialog.set_focus()
                break
    except Exception as e:
        print(f"⚠️ Failed to refocus: {e}")

def track_active_window():
    """Track the currently active window and restart if a new one is detected."""
    global last_active_title
    while True:
        try:
            win = gw.getActiveWindow()
            if win and win.title and win.title != last_active_title:
                print(f"🆕 New active window detected: {win.title}")
                last_active_title = win.title
                # restart_app()  # Restart the app when a new window is detected
        except Exception as e:
            print(f"⚠️ Error tracking active window: {e}")
        time.sleep(0.5)

def refocus_last_window():
    global last_active_title
    try:
        if last_active_title:
            win = gw.getWindowsWithTitle(last_active_title)
            if win:
                win[0].activate()
                print(f"🔁 Refocused: {last_active_title}")
    except Exception as e:
        print(f"⚠️ Could not refocus: {e}")