import socket
import psutil
import time
import json

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        cpu_percent = psutil.cpu_percent()
        msg = dict(cpu_percent=cpu_percent)
        msg_json = json.dumps(msg)
        s.sendall(msg_json.encode())
        print(s.recv(1024).decode())
        time.sleep(1)
