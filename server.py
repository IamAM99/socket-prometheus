import threading
import socket
import json
import time
from prometheus_client import start_http_server, Gauge, Counter

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
PROMETHEUS_PORT = 8000


def client_thread(conn, addr, metrics):
    addr_str = str(addr[0]) + ":" + str(addr[1])
    with conn:
        print(f"[CONNECTION] {addr_str} connected.")
        while True:
            try:
                # send acknowledgement to the clinet
                conn.sendall(json.dumps({"server_time": time.time()}).encode())

                # receive the message from the client
                msg = conn.recv(1024)
                if not msg:
                    break
                msg = json.loads(msg.decode())
                print(f"[{addr_str}] Data received!")

                # get the agent name (it is IP:PORT in our clients)
                agent_name = msg.pop("agent")

                # pass the metrics to prometheus
                for metric in metrics:
                    val = msg[metric._name]["val"]
                    metric_type = msg[metric._name]["type"]

                    if metric_type == "gauge":
                        metric.labels(agent_name).set(val)
                    elif metric_type == "counter":
                        metric.labels(agent_name).inc(val)

            except ConnectionError:
                print(f"[FAILED] {addr_str} connection interrupted")
                break

    print(f"[CONNECTION] {addr_str} disconnected.")


if __name__ == "__main__":
    # prometheus metric names
    metric_names = {
        "number_msg_sent_count": "counter",
        "ping_to_8_8_8_8_ms": "gauge",
        "delay_to_server_seconds": "gauge",
        "cpu_usage_percent": "gauge",
        "cpu_freq_Mhz": "gauge",
        "virtual_memory_usage_percent": "gauge",
        "swap_memory_usage_percent": "gauge",
        "network_sent_bytes": "gauge",
        "network_recv_bytes": "gauge",
        "network_sent_packets_count": "gauge",
        "network_recv_packets_count": "gauge",
    }

    # initialize prometheus metrics
    metrics = []
    for name, metric_type in metric_names.items():
        if metric_type == "gauge":
            metrics.append(Gauge(name, "", ["adr"]))
        elif metric_type == "counter":
            metrics.append(Counter(name, "", ["adr"]))

    # start the prometheus client
    start_http_server(PROMETHEUS_PORT)

    # start the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=client_thread, args=(conn, addr, metrics)).start()
