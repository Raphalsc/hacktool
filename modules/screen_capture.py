# modules/screen_capture.py

import mss
import io
from PIL import Image

def take_screenshot():
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])  # tout l’écran principal
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
