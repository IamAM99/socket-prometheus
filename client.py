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
        self.msg = json.dumps({self.name: val})

    def run(self, interval=1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            while True:
                s.sendall(self.msg.encode())
                response = json.loads(s.recv(1024).decode())
                self.msg = json.dumps({self.name: self.val(**response)})
                print(f"[{self.name}] {response}")
                time.sleep(interval)


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
