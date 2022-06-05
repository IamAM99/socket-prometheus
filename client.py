import threading

# import agents
import socket
import psutil
import time
import json

# import os


HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
INTERVAL = 1  # seconds


class Agent:
    def __init__(self, data_gen: dict, metric_type: str):
        self.data_gen = data_gen
        self.type = metric_type
        self.adr = "unknown"  # after connecting, it will be 'IP:PORT'

    def _get_data(self):
        data = {}
        for metric, generator in self.data_gen.items():
            data[metric] = generator()
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
                    msg = {"agent": self.adr, "type": self.type}
                    msg.update(self._get_data())
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


if __name__ == "__main__":
    data_gen = dict(
        cpu_usage_percent=lambda *args, **kwargs: psutil.cpu_percent(),
        cpu_freq_Mhz=lambda *args, **kwargs: psutil.cpu_freq().current,
    )
    agent = Agent(data_gen, "gauge")

    agent.run()
