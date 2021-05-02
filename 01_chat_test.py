import socket
import select
import sys
import threading


class ServerTest():
    def __init__(self) -> None:
        with open("ip.txt") as f:
            ip = f.readline()
        port = 1351

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(ip, port)

        self.server.listen(100)

        list_clients = []

    def client_thread(self, connection, address):
        connection.send("Test")

        while True:
            try:
                message = connection.recv(2048)
                if message:
                    print("<" + address[0] + "> " + message)

                    message_to_send = "<" + address[0] + "> " + message
                    self.broadcast(message_to_send, connection)
                else:
                    self.remove(connection)
            except:
                continue
