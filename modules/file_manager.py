# modules/file_manager.py

import os
import base64

def list_directory(path="."):
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Erreur : {e}"

def read_file(path):
    try:
        with open(path, "rb") as f:
            content = f.read()
        return base64.b64encode(content)
    except Exception as e:
        return str(e).encode()
