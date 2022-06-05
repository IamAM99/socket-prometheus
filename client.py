import platform
import socket
import psutil
import time
import json
import os


HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
INTERVAL = 2  # seconds


class Agent:
    def __init__(self, data_gen: dict):
        self.data_gen = data_gen
        self.adr = "unknown"  # after connecting, it will be 'IP:PORT'

    def _get_data(self, response):
        data = {}
        for metric, generator in self.data_gen.items():
            data[metric] = {
                "val": generator["gen"](**response),
                "type": generator["type"],
            }
        return data

    def _connect(self, s, addr, interval):
        while True:
            try:
                s.connect(addr)
                break
            except socket.error:
                print(f"[FAILED] Connection failed for agent '{self.adr}', retrying...")
                time.sleep(interval)

    def run(self, interval=INTERVAL):
        retry = False

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self._connect(s, (HOST, PORT), interval)
            self.adr = str(s.getsockname()[0]) + ":" + str(s.getsockname()[1])

            while True:
                response = s.recv(1024).decode()

                if response:
                    # print the server response
                    response = json.loads(response)
                    print(f"[{self.adr}] {response}")

                    # create the message json
                    msg = {"agent": self.adr}
                    msg.update(self._get_data(response))
                    self.msg = json.dumps(msg)

                    # send the message
                    s.sendall(self.msg.encode())
                else:
                    print(
                        f"[FAILED] Received empty message for agent '{self.adr}', reconnecting..."
                    )

                    # reconnect after 'interval' seconds
                    time.sleep(interval)
                    retry = True
                    break

                time.sleep(interval)

            if retry:
                self.run(interval)


def ping(ip: str = "www.google.com", *args, **kwargs):
    if platform.system().lower() == "windows":
        p = "-n"
    else:
        p = "-c"
    command = "ping " + p + "1 " + ip
    ping = os.popen(command)
    ping = ping.readlines()[1]
    ping = float(ping[ping.find("time=") + 5 : ping.find("ms")].strip())
    return ping


if __name__ == "__main__":
    data_gen = dict(
        number_msg_sent_count={"gen": lambda *args, **kwargs: 1, "type": "counter",},
        ping_to_google_ms={"gen": ping, "type": "gauge",},
        delay_to_server_seconds={
            "gen": lambda server_time, *args, **kwargs: time.time() - server_time,
            "type": "gauge",
        },
        cpu_usage_percent={
            "gen": lambda *args, **kwargs: psutil.cpu_percent(),
            "type": "gauge",
        },
        cpu_freq_Mhz={
            "gen": lambda *args, **kwargs: psutil.cpu_freq().current,
            "type": "gauge",
        },
        virtual_memory_usage_percent={
            "gen": lambda *args, **kwargs: psutil.virtual_memory().percent,
            "type": "gauge",
        },
        swap_memory_usage_percent={
            "gen": lambda *args, **kwargs: psutil.swap_memory().percent,
            "type": "gauge",
        },
        network_sent_bytes={
            "gen": lambda *args, **kwargs: psutil.net_io_counters().bytes_sent,
            "type": "gauge",
        },
        network_recv_bytes={
            "gen": lambda *args, **kwargs: psutil.net_io_counters().bytes_recv,
            "type": "gauge",
        },
        network_sent_packets_count={
            "gen": lambda *args, **kwargs: psutil.net_io_counters().packets_sent,
            "type": "gauge",
        },
        network_recv_packets_count={
            "gen": lambda *args, **kwargs: psutil.net_io_counters().packets_recv,
            "type": "gauge",
        },
    )
    agent = Agent(data_gen)

    agent.run()
