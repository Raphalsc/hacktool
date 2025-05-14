import base64

END_MARKER = b"<END>"

def send_data(sock, data):
    """
    Envoie des données (str ou bytes) avec un marqueur de fin.
    """
    if isinstance(data, str):
        data = data.encode()
    sock.sendall(data + END_MARKER)

def receive_data(sock):
    """
    Reçoit des données jusqu'au marqueur de fin.
    """
    data = b""
    while True:
        part = sock.recv(4096)
        if part.endswith(END_MARKER):
            data += part[:-len(END_MARKER)]
            break
        data += part
    return data

def send_base64(sock, binary_data):
    """
    Encode des données binaires en base64 et les envoie.
    """
    encoded = base64.b64encode(binary_data)
    send_data(sock, encoded)

def receive_base64(sock):
    """
    Reçoit des données encodées en base64 et les décode.
    """
    encoded = receive_data(sock)
    return base64.b64decode(encoded)
