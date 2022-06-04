import threading
import socket
import json
import time
from prometheus_client import start_http_server, Gauge

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
PROMETHEUS_PORT = 8000
g = Gauge("agent_cpu_percent", "CPU usage percentage of the client")
g.set(0.0)


def client_thread(conn, addr):
    with conn:
        print(f"[CONNECTION] {addr} connected.")
        while True:
            data = conn.recv(2048)
            if not data:
                break
            msg = json.loads(data.decode())
            print(f"[{addr[0]}:{addr[1]}] {msg}")
            # g.set(msg["cpu_percent"])
            conn.sendall(
                json.dumps({"host_time": time.time(), "status": "ACK"}).encode()
            )
    print(f"[CONNECTION] {addr} disconnected.")


if __name__ == "__main__":
    start_http_server(PROMETHEUS_PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=client_thread, args=(conn, addr)).start()
