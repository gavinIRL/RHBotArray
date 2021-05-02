import socket
import select
import sys
import _thread
from time import sleep


class ClientTest():
    def __init__(self) -> None:
        with open("ip.txt") as f:
            ip = f.readline()
        port = 1351

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((ip, port))
        self.sockets_list = []

    def start(self):
        while True:
            self.sockets_list = [socket.socket(), self.server]
            read_socks, write_sock, err_sock = select.select(
                self.sockets_list, [], [])

            for socks in read_socks:
                if socks == self.server:
                    message = socks.recv(2048)
                    print(message)
                    sleep(0.01)
                else:
                    message = sys.stdin.readline()
                    self.server.send(message)
                    sys.stdout.write("<You>")
                    sys.stdout.write(message)
                    sys.stdout.flush()
                    sleep(0.01)


if __name__ == "__main__":
    client = ClientTest()
    client.start()
    client.server.close()
