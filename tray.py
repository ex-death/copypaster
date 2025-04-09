from PIL import Image, ImageDraw
import pystray
import pyperclip
from threading import Thread
import paste
import capture
import os
from utils import refocus_last_window
from config import load_config, save_config

# Global variables
tray_icon = None
shared_data = {
    "copied_text": ""  # Initialize with an empty string
}

copied_text = pyperclip.paste()
config = load_config()
show_copied_text = config.get("show_copied_text", True)
notifications_enabled = config.get("notifications_enabled", True)

def create_image():
    """Create a clipboard icon for the system tray."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw clipboard base (rectangle)
    draw.rectangle((12, 16, 52, 56), fill="white", outline="black", width=2)

    # Draw clipboard clip (top part)
    draw.rectangle((20, 8, 44, 16), fill="gray", outline="black", width=2)

    # Add lines to represent text on the clipboard
    draw.line((16, 24, 48, 24), fill="black", width=1)  # Line 1
    draw.line((16, 32, 48, 32), fill="black", width=1)  # Line 2
    draw.line((16, 40, 48, 40), fill="black", width=1)  # Line 3
    draw.line((16, 48, 48, 48), fill="black", width=1)  # Line 4
# Resize to standard icon sizes (optional)
    # icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
    # img.save("icon.ico", format="ICO", sizes=icon_sizes)
    return img

def on_copy(icon, item):
    """Handle the Copy action."""
    global copied_text
    copied_text = capture.capture_and_extract_text()
    if notifications_enabled:
        print(f"{copied_text}")
    return 0

def on_paste(icon, item):
    """Handle the Paste action."""
    refocus_last_window()
    paste.paste_text()
    return 0

def on_quit(icon, item):
    """Quit the application."""
    icon.visible = False
    icon.stop()
    print("🛑 Quitting application...")
    os._exit(0)
    return 0

def update_menu():
    """Update the tray menu dynamically."""
    global tray_icon
    copied_text = pyperclip.paste()
    tray_icon.menu = pystray.Menu(
        pystray.MenuItem(
            f"{copied_text[:100]}..." if show_copied_text and len(copied_text) > 100 else f"{copied_text}" if show_copied_text else "📋 Copied text hidden",
            lambda: None,
            enabled=False
        ),
        pystray.MenuItem("📋 Copy", on_copy),
        pystray.MenuItem("⌨️ Paste", on_paste),
        pystray.MenuItem(
            f"🔔 Notifications {'✅' if notifications_enabled else '❌'}", toggle_notifications
        ),
        pystray.MenuItem(
            f"👁️ Copied Text {'✅' if show_copied_text else '❌'}", toggle_copied_text
        ),
        pystray.MenuItem("❌ Quit", on_quit)
    )
    tray_icon.update_menu()

def toggle_notifications(icon, item):
    """Toggle notifications on or off."""
    global notifications_enabled
    notifications_enabled = not notifications_enabled
    config["notifications_enabled"] = notifications_enabled
    save_config(config)
    print(f"🔔 Notifications {'enabled' if notifications_enabled else 'disabled'}")
    update_menu()  # Update the menu to reflect the change

def toggle_copied_text(icon, item):
    """Toggle showing the copied text in the tray menu."""
    global show_copied_text
    show_copied_text = not show_copied_text
    config["show_copied_text"] = show_copied_text
    save_config(config)
    print(f"📋 Copied text display {'enabled' if show_copied_text else 'disabled'}")
    update_menu()  # Update the menu to reflect the change

def run_tray():
    """Run the system tray icon."""
    global tray_icon  # Use the global variable

    tray_icon = pystray.Icon(
        "CopyPaster",
        create_image(),
        menu=pystray.Menu(
            pystray.MenuItem(
                f"{copied_text[:100]}..." if show_copied_text and len(copied_text) > 100 else f"{copied_text}" if show_copied_text else "📋 Copied text hidden",
                lambda: None,
                enabled=False
            ),
            pystray.MenuItem("📋 Copy", on_copy),
            pystray.MenuItem("⌨️ Paste", on_paste),
            pystray.MenuItem(
                f"🔔 Notifications {'✅' if notifications_enabled else '❌'}", toggle_notifications
            ),
            pystray.MenuItem(
                f"👁️ Copied Text {'✅' if show_copied_text else '❌'}", toggle_copied_text
            ),
            pystray.MenuItem("❌ Quit", on_quit)
        )
    )
    tray_icon.run()

def start_tray_thread():
    """Start the system tray icon in a separate thread."""
    Thread(target=run_tray, daemon=True).start()

def on_left_click(icon, item):
    """Handle left-click on the tray icon."""
    print("👈 Left click detected - pasting")
    refocus_last_window()
    paste.paste_text()
