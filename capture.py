import time
import pytesseract
import pyperclip
import threading
import numpy as np
from PIL import Image, ImageGrab
import cv2
import tkinter as tk
import win10toast
from screeninfo import get_monitors
from utils import screen_grab_win32
# from plyer import notification
from win10toast import ToastNotifier

# Initialize the notifier
toaster = ToastNotifier()
# Create a lock for the toaster
toaster_lock = threading.Lock()

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class SnipTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-alpha", 0.3)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.monitors = get_monitors()
        self.min_x = min(m.x for m in self.monitors)
        self.min_y = min(m.y for m in self.monitors)
        self.max_x = max(m.x + m.width for m in self.monitors)
        self.max_y = max(m.y + m.height for m in self.monitors)

        width = self.max_x - self.min_x
        height = self.max_y - self.min_y
        self.root.geometry(f"{width}x{height}+{self.min_x}+{self.min_y}")

        self.start_x = None
        self.start_y = None
        self.rect_id = None

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.root.mainloop()

    def on_press(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.rect_id = self.canvas.create_rectangle(
            self.start_x - self.min_x, self.start_y - self.min_y,
            self.start_x - self.min_x, self.start_y - self.min_y,
            outline="red", width=2
        )

    def on_drag(self, event):
        end_x = event.x_root
        end_y = event.y_root
        self.canvas.coords(
            self.rect_id,
            self.start_x - self.min_x, self.start_y - self.min_y,
            end_x - self.min_x, end_y - self.min_y
        )

    def on_release(self, event):
        end_x = event.x_root
        end_y = event.y_root
        self.root.withdraw()
        time.sleep(0.2)

        bbox = (
            min(self.start_x, end_x),
            min(self.start_y, end_y),
            max(self.start_x, end_x),
            max(self.start_y, end_y)
        )

        try:
            screenshot = screen_grab_win32(bbox)
            # screenshot.save("debug_original.png")
            # print("💾 Original screenshot saved as debug_original.png")

            processed = self.preprocess_image(screenshot)
            # processed.save("debug_processed.png")
            # print("💾 Processed image saved as debug_processed.png")

            # screenshot.show(title="Original Capture")
            # processed.show(title="Processed for OCR")

            extracted_text = pytesseract.image_to_string(
                processed,
                lang="eng",
                config='--oem 3 --psm 6 --dpi 300 -c preserve_interword_spaces=1'
            ).strip()

            extracted_text = extracted_text.replace("|", "| ")
            pyperclip.copy(extracted_text)
            print(f"📋 Copied to Clipboard: {extracted_text}")
            # self.show_notification(f"Copied to clipboard:\n{extracted_text[:100]}")
            # Show a notification with the copied text
            # notification.notify(
            #     title="Text Copied",
            #     message=f"{extracted_text[:100]}..." if len(extracted_text) > 100 else extracted_text,
            #     timeout=5  # Notification duration in seconds
            # )
             # Define a callback function for the notification click
            def on_notification_click():
                print("DEBUG: Notification clicked!")
            # Add any additional behavior here, such as refocusing a window
# Use a lock to synchronize access to the toaster
            with toaster_lock:
                toaster.show_toast(
                    "Text Copied",
                    f"{extracted_text[:100]}..." if len(extracted_text) > 100 else extracted_text,
                    icon_path="C:\\Users\\work brand\\OneDrive - Modo Networks\\Program\\CopyPasta\\icon.ico",
                    duration=3,
                    threaded=True,
                )


        except Exception as e:
            print(f"❌ Error during capture: {e}")
        finally:
            self.root.destroy()

    def preprocess_image(self, pil_image):
        gray = pil_image.convert("L")
        scale = 2.5 if gray.width < 400 or gray.height < 100 else 2.0
        resized = gray.resize((int(gray.width * scale), int(gray.height * scale)), Image.LANCZOS)

        np_image = np.array(resized)
        _, processed = cv2.threshold(np_image, 170, 255, cv2.THRESH_BINARY)
        return Image.fromarray(processed)
    
    # def show_notification(self, text, duration=2000):
    #     notif = tk.Toplevel()
    #     notif.overrideredirect(True)
    #     notif.attributes("-topmost", True)
    #     notif.configure(bg="black")

    #     # Position near bottom right corner of primary monitor
    #     x = self.max_x - 300
    #     y = self.max_y - 100
    #     notif.geometry(f"300x50+{x}+{y}")

    #     label = tk.Label(notif, text=text, bg="black", fg="white", font=("Segoe UI", 10))
    #     label.pack(expand=True, fill=tk.BOTH)

    #     notif.after(duration, notif.destroy)


def capture_and_extract_text():
    SnipTool()
