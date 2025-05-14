# modules/screen_capture.py

import pyautogui
import io

def take_screenshot():
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return buffer.getvalue()
