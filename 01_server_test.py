import socket
import select
import sys
import _thread


class ServerTest():
    def __init__(self) -> None:
        with open("ip.txt") as f:
            ip = f.readline()
        port = 1351

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip, port))

        self.server.listen(100)

        self.list_clients = []

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

    def broadcast(self, message, connection):
        for clients in self.list_clients:
            if clients != connection:
                try:
                    clients.send(message)
                except:
                    clients.close()

                    # if the link is broken, we remove the client
                    self.remove(clients)

    def remove(self, connection):
        if connection in self.list_clients:
            self.list_clients.remove(connection)

    def start(self):
        while True:
            connection, address = self.server.accept()

            self.list_clients.append(connection)

            print(address[0] + " connected")
            _thread.start_new_thread(self.client_thread, (connection, address))
        self.server.close()
