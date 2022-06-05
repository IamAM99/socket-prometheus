import threading
import socket
import json
import time
from prometheus_client import start_http_server, Gauge, Counter

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
PROMETHEUS_PORT = 8000


def client_thread(conn, addr):
    metrics = []
    addr_str = str(addr[0]) + ":" + str(addr[1])
    with conn:
        print(f"[CONNECTION] {addr_str} connected.")
        while True:
            try:
                # send acknowledgement to the clinet
                conn.sendall(json.dumps({"host_time": time.time()}).encode())

                # receive the message from the client
                msg = conn.recv(1024)
                if not msg:
                    break
                msg = json.loads(msg.decode())
                print(f"[{addr_str}] Data received!")

                # make key names correspond to agent IP:PORT
                agent = msg.pop("agent")
                agent = agent.replace(".", "_").replace(":", "_")
                for key in list(msg):
                    msg["agent_" + agent + "_" + key] = msg.pop(key)

                # set the prometheus metrics
                if not metrics:
                    for key in msg:
                        metric_type = msg[key]["type"]
                        if metric_type == "gauge":
                            metrics.append(Gauge(key, ""))
                        elif metric_type == "counter":
                            metrics.append(Counter(key, ""))

                for metric in metrics:
                    val = msg[metric._name]["val"]
                    metric_type = msg[metric._name]["type"]

                    if metric_type == "gauge":
                        metric.set(val)
                    elif metric_type == "counter":
                        metric.inc(val)

            except ConnectionError:
                print(f"[FAILED] {addr_str} connection interrupted")
                break

    print(f"[CONNECTION] {addr_str} disconnected.")


if __name__ == "__main__":
    start_http_server(PROMETHEUS_PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            print("hey")
            threading.Thread(target=client_thread, args=(conn, addr)).start()
