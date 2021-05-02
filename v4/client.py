import socket
import select
import errno
import sys
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
from random import randint


class ListenClientTest():
    def __init__(self) -> None:
        self.HEADER_LENGTH = 10
        with open("ip.txt") as f:
            self.IP = f.readline()
        self.PORT = 1351
        self.my_username = "Testy Test "+str(randint(100, 1000))

        # Create a socket
        # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
        # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to a given ip and port
        self.client_socket.connect((self.IP, self.PORT))

        # Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
        self.client_socket.setblocking(False)

        # Prepare username and header and send them
        # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
        username = self.my_username.encode('utf-8')
        username_header = f"{len(username):<{self.HEADER_LENGTH}}".encode(
            'utf-8')
        self.client_socket.send(username_header + username)

    def send_message(self, message):
        message = message.encode('utf-8')
        message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode(
            'utf-8')
        self.client_socket.send(message_header + message)

    def main_loop(self):
        while True:
            # Wait for user to input a message
            message = input(f'{self.my_username} > ')

            # If message is not empty - send it
            if message:

                # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                message = message.encode('utf-8')
                message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode(
                    'utf-8')
                self.client_socket.send(message_header + message)

            try:
                # Now we want to loop over received messages (there might be more than one) and print them
                while True:

                    # Receive our "header" containing username length, it's size is defined and constant
                    username_header = self.client_socket.recv(
                        self.HEADER_LENGTH)
                    # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                    if not len(username_header):
                        print('Connection closed by the server')
                        sys.exit()
                    # Convert header to int value
                    username_length = int(
                        username_header.decode('utf-8').strip())
                    # Receive and decode username
                    username = self.client_socket.recv(
                        username_length).decode('utf-8')
                    # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                    message_header = self.client_socket.recv(
                        self.HEADER_LENGTH)
                    message_length = int(
                        message_header.decode('utf-8').strip())
                    message = self.client_socket.recv(
                        message_length).decode('utf-8')
                    # Print message
                    print(f'{username} > {message}')

            except IOError as e:
                # This is normal on non blocking connections - when there are no incoming data error is going to be raised
                # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
                # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
                # If we got different error code - something happened
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()
                # We just did not receive anything
                continue
            except Exception as e:
                # Any other exception - something happened, exit
                print('Reading error: '.format(str(e)))
                sys.exit()


class ClientKeypressListener():
    def __init__(self, client) -> None:
        self.client = client
        self.listener = None
        self.unreleased_keys = []

    def start_keypress_listener(self):
        if self.listener == None:
            self.listener = Listener(on_press=self.on_press,
                                     on_release=self.on_release)
            self.listener.start()

    def on_press(self, key):
        if str(key) not in self.unreleased_keys:
            self.client.send_message(str(key)+",down")
            self.unreleased_keys.append(str(key))

    def on_release(self, key):
        self.client.send_message(str(key)+",up")
        self.unreleased_keys.remove(str(key))


if __name__ == "__main__":
    lct = ListenClientTest()
    ckl = ClientKeypressListener(lct)
    ckl.start_keypress_listener()
    lct.main_loop()
