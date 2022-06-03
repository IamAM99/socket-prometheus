import socket


HOST = socket.gethostname()
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(data.decode())
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
