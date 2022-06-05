import threading
import socket
import psutil
import time
import json

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080


class Agent:
    def __init__(self, name, val_generator, default=None):
        self.name = name
        self.val = val_generator
        if default is None:
            val = self.val()
        else:
            val = default
        self.msg = json.dumps({"name": self.name, "value": val})

    def _connect(self, s, addr):
        while True:
            try:
                s.connect(addr)
                break
            except socket.error:
                print(
                    f"[FAILED] Connection failed for agent '{self.name}', retrying..."
                )
                time.sleep(1)

    def run(self, interval=1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self._connect(s, (HOST, PORT))

            while True:
                s.sendall(self.msg.encode())
                response = s.recv(1024).decode()
                if response:
                    response = json.loads(response)
                    self.msg = json.dumps(
                        {"name": self.name, "value": self.val(**response)}
                    )
                    print(f"[{self.name}] {response}")
                else:
                    print(
                        f"[FAILED] Received empty message for agent '{self.name}', reconnecting..."
                    )
                    time.sleep(1)
                    retry = True
                    break
                time.sleep(interval)
            if retry:
                self.run()


if __name__ == "__main__":
    agents = []
    agents.append(
        Agent("agent_cpu_usage_percent", lambda *args, **kwargs: psutil.cpu_percent())
    )
    agents.append(
        Agent(
            "agent_delay_seconds",
            lambda host_time, *args, **kwargs: time.time() - host_time,
            default=0,
        )
    )

    for agent in agents:
        threading.Thread(target=agent.run, args=()).start()
