import socket
import json
from prometheus_client import start_http_server, Gauge

HOST = socket.gethostname()
PORT = 8080
PROMETHEUS_PORT = 8000
g = Gauge("cpu_percent", "CPU usage percentage of the client")
g.set(0.0)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    start_http_server(PROMETHEUS_PORT)

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                msg = json.loads(data.decode())
                print(msg)
                g.set(msg["cpu_percent"])
                conn.sendall("ACK".encode())
        print("Disconnected")

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((socket.gethostname(), 12314))
#     s.listen(5)
#     while True:
#         conn, addr = s.accept()
#         with conn:
#             print(f"Connection from {addr} has been established!")

#             msg = "Welcome to the server!"
#             msg = f"{len(msg):<{HEADERSIZE}}" + msg
#             print(msg)

#             conn.send(bytes(msg, "utf-8"))
