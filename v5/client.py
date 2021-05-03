import socket
import select
import errno
import sys
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
from random import randint
import subprocess
import threading
import time
import os


class RHBotClientConnection():
    def __init__(self, ip, delay=0) -> None:

        self.delay = delay
        self.HEADER_LENGTH = 10
        self.IP = ip
        self.PORT = 1351
        self.my_username = "Testy Test "+str(randint(100, 1000))

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket.connect((self.IP, self.PORT))

        self.client_socket.setblocking(False)

        username = self.my_username.encode('utf-8')
        username_header = f"{len(username):<{self.HEADER_LENGTH}}".encode(
            'utf-8')
        self.client_socket.send(username_header + username)

    def send_message(self, message):
        if self.delay > 0:
            self.send_message_delayed(message, self.delay)
        else:
            message = message.encode('utf-8')
            message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode(
                'utf-8')
            self.client_socket.send(message_header + message)

    def send_message_delayed(self, message, delay):
        start_time = time.time()
        t = threading.Thread(target=self.delay_thread,
                             args=(message, delay, start_time))
        t.start()

    def delay_thread(self, message, delay, start_time):
        message = message.encode('utf-8')
        message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode(
            'utf-8')
        time.sleep(delay - (time.time()-start_time))
        self.client_socket.send(message_header + message)

    def main_loop(self):
        while True:
            time.sleep(0.5)


class ClientKeypressListener():
    def __init__(self, list_servers) -> None:
        self.list_servers = list_servers
        self.listener = None
        self.unreleased_keys = []

    def start_keypress_listener(self):
        if self.listener == None:
            self.listener = Listener(on_press=self.on_press,
                                     on_release=self.on_release)
            self.listener.start()

    def on_press(self, key):
        if str(key) not in self.unreleased_keys:
            for server in self.list_servers:
                server.send_message(str(key)+",down")
            self.unreleased_keys.append(str(key))

    def on_release(self, key):
        for server in self.list_servers:
            server.send_message(str(key)+",up")
        self.unreleased_keys.remove(str(key))

        if key == keyboard.Key.f4:
            self.bot_running = False
            # self.combatbat.running = False
            # Need to pause for 1 second and then clear all keypresses
            time.sleep(0.5)
            # self.combatbat.remove_all_keypresses()
            print("Exiting bot")
            os._exit(1)


class ClientUtils():
    def grab_online_servers():
        output = subprocess.run("arp -a", capture_output=True).stdout.decode()
        list_ips = []
        with open("servers.txt", "r") as f:
            lines = f.readlines()
            for ip in lines:
                if ip.strip() in output:
                    list_ips.append(ip.strip())
        return list_ips

    def start_server_thread(server):
        t = threading.Thread(target=server.main_loop(), daemon=True)
        t.start()


class RHBotClient():
    def start(delay_min=0, delay_spacing=5):
        list_ips = ClientUtils.grab_online_servers()
        list_servers = []
        for i, ip in enumerate(list_ips):
            if delay_min == 0:
                list_servers.append(RHBotClientConnection(ip))
            else:
                list_servers.append(RHBotClientConnection(
                    ip, delay_min+i*delay_spacing))
        ckl = ClientKeypressListener(list_servers)
        ckl.start_keypress_listener()
        for server in list_servers:
            ClientUtils.start_server_thread(server)
        while True:
            time.sleep(1)


if __name__ == "__main__":
    RHBotClient.start()
