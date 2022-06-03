import socket
import psutil
import time
import json

HOST = socket.gethostname()
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


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((socket.gethostname(), 12314))

#     while True:
#         full_msg = ""
#         new_msg = True
#         while True:
#             msg = s.recv(16)
#             if new_msg:
#                 print(f"New message length: {msg[:HEADERSIZE]}")
#                 msglen = int(msg[:HEADERSIZE])
#                 new_msg = False

#             full_msg += msg.decode("utf-8")

#             if len(full_msg) - HEADERSIZE == msglen:
#                 print("full msg recvd")
#                 print(full_msg[HEADERSIZE:])
#                 new_msg = True
#                 full_msg = ""

#         print(full_msg)
