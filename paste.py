import pyperclip
import time
from pynput import mouse
from pynput.keyboard import Controller, Key
import keyboard

kb = Controller()
pasting = False
last_paste_time = 0
should_stop_pasting = False

def release_modifiers():
    for key in ["ctrl", "alt", "v"]:
        if keyboard.is_pressed(key):
            keyboard.release(key)

def type_with_shift(char):
    shift_symbols = {
        '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
        '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
        '_': '-', '+': '=', '{': '[', '}': ']', '|': '\\',
        ':': ';', '"': "'", '<': ',', '>': '.', '?': '/'
    }
    if char in shift_symbols or char.isupper():
        with kb.pressed(Key.shift):
            kb.type(shift_symbols.get(char, char.lower()))
    else:
        kb.type(char)

def on_click(x, y, button, pressed):
    global should_stop_pasting
    if pasting and pressed:
        should_stop_pasting = True
        print("⚠️ Click detected - stopping paste")

mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

def paste_text():
    global pasting, last_paste_time, should_stop_pasting
    if pasting or (time.time() - last_paste_time) < 1:
        return

    pasting = True
    should_stop_pasting = False
    last_paste_time = time.time()

    release_modifiers()
    time.sleep(0.1)

    try:
        clipboard_content = pyperclip.paste()
        if clipboard_content:
            print(f"⌨️ Pasting: {clipboard_content}")
            for char in clipboard_content:
                if should_stop_pasting:
                    print("✋ Paste interrupted")
                    break
                type_with_shift(char)
    finally:
        pasting = False
        should_stop_pasting = False
