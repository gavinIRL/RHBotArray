import socket
import select
import threading
from rhba_utils import BotUtils, Events, QuestHandle, SellRepair, WindowCapture, Follower
import pydirectinput
import time
import os
import ctypes
from cryptography.fernet import Fernet
from fuzzywuzzy import process
from custom_input import CustomInput

# Change directory to current file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class RHBotArrayServer():
    def __init__(self, print_only=False, move_only=False, support=True) -> None:
        self.print_only = print_only
        self.support = support
        self.move_only = move_only
        self.move_only_exclude_keys = ["a", "s", "d", "f", "g", "h"]

        with open("gamename.txt") as f:
            self.gamename = f.readline()

        self.HEADER_LENGTH = 10
        self.IP = BotUtils.grab_current_lan_ip()
        self.PORT = 1351

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        self.sockets_list = [self.server_socket]
        self.clients = {}
        print(f'Listening for connections on {self.IP}:{self.PORT}...')

        with open("key.key") as f:
            key = f.read()
        self.fern = Fernet(key)

        self.last_mouse_move = time.time() - 10

        # These are related to the autoloot function
        self.autoloot_enabled = False

        # These are related to the questhandling
        self.quest_handle = QuestHandle()
        self.sell_repair = SellRepair()

        # These are related to allow x in all cases
        self.allowx = False

        # These are for the v2 regroup command
        self.map_rect = None
        self.level_name = None
        self.speed = 20
        self.rects, self.speeds = BotUtils.grab_level_rects_and_speeds()
        self.player_pos = None
        self.regroup_try_count = 0

        # This is for the pag vs custom input town mode
        # False means custom mode, true means pag
        self.inputmode = False

        # This is for follow mode
        self.followmode = False
        self.follower = Follower()

    def auto_loot(self):
        consec_xpress = 0
        while self.autoloot_enabled:
            if self.loot_if_available():
                consec_xpress += 1
                if not consec_xpress > 6:
                    time.sleep(0.01)
                    CustomInput.release_key(CustomInput.key_map["x"])
                    time.sleep(0.425)
                else:
                    time.sleep(0.4)
            else:
                time.sleep(0.1)
                consec_xpress = 0

    def autoloot_thread_start(self):
        t = threading.Thread(target=self.auto_loot, daemon=True)
        self.autoloot_enabled = True
        t.start()

    def loot_if_available(self):
        if BotUtils.detect_xprompt(self.gamename):
            CustomInput.press_key(CustomInput.key_map["x"])
            return True
        return False

    def batch_handle(self, lines: str):
        data = lines.split("\n")
        data.pop(0)
        converted = []
        # now convert each line into a list
        for line in data:
            converted.append(line.rstrip('\n').split("|"))
        # first sleep until the first action time
        # print(converted)
        try:
            time.sleep(float(converted[0][2]))
            for idx, line in enumerate(converted):
                action_start_time = time.time()
                # do the action
                if line[1] == "keyDown":
                    # print("Would press {} down now".format(line[0]))
                    k = BotUtils.convert_pynput_to_pag(line[0].strip("'"))
                    pydirectinput.keyDown(k)
                elif line[1] == "keyUp":
                    # print("Would press {} down now".format(line[0]))
                    k = BotUtils.convert_pynput_to_pag(line[0].strip("'"))
                    pydirectinput.keyUp(k)
                elif line[1] == "click":
                    xrat, yrat = line[3].split(",")
                    # print("Would click at {},{} now".format(x, y))
                    x, y = BotUtils.convert_window_to_true(self.gamename,
                                                           float(xrat), float(yrat))
                    x = int(x)
                    y = int(y)
                    # pydirectinput.click(x, y, duration=0.025)
                    ctypes.windll.user32.SetCursorPos(x, y)
                    if line[0] == "Button.left":
                        ctypes.windll.user32.mouse_event(
                            0x0002, 0, 0, 0, 0)
                        ctypes.windll.user32.mouse_event(
                            0x0004, 0, 0, 0, 0)
                    elif line[0] == "Button.right":
                        pydirectinput.rightClick(duration=0.01)
                if line[1] == "questhandle":
                    self.quest_handle.start_quest_handle()
                try:
                    next_action = converted[idx + 1]
                    if next_action[0] == "":
                        break
                except IndexError:
                    # this was the last action in the list
                    break
                elapsed_time = float(next_action[2]) - float(line[2])
                elapsed_time -= (time.time() - action_start_time)
                if elapsed_time < 0:
                    elapsed_time = 0

                time.sleep(elapsed_time)
        except:
            # This will only occur if there is an empty batch
            pass

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(self.HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except:
            return False

    def start(self):
        while True:
            read_sockets, _, exception_sockets = select.select(
                self.sockets_list, [], self.sockets_list)
            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()
                    user = self.receive_message(client_socket)
                    if user is False:
                        continue
                    self.sockets_list.append(client_socket)
                    self.clients[client_socket] = user
                    print('Accepted new connection from {}:{}, username: {}'.format(
                        *client_address, user['data'].decode('utf-8')))
                # Else existing socket is sending a message
                else:
                    message = self.receive_message(notified_socket)
                    if message is False:
                        print('Closed connection from: {}'.format(
                            self.clients[notified_socket]['data'].decode('utf-8')))
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue
                    decrypted = self.fern.decrypt(message["data"])
                    self.do_message_checks(decrypted)

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients[notified_socket]

    def do_message_checks(self, decrypted: bytes):
        if self.print_only:
            print(decrypted.decode())
        else:
            if (time.time() - self.last_mouse_move) >= 10:
                BotUtils.move_mouse_centre(self.gamename)
                self.last_mouse_move = time.time()
            button, direction = str(
                decrypted.decode("utf-8")).split(",", 1)
            if button == "Button.left":
                xrat, yrat = direction.split("|")
                # Need to convert from ratio to click
                x, y = BotUtils.convert_window_to_true(self.gamename,
                                                       float(xrat), float(yrat))
                # and then click at that location
                x = int(x)
                y = int(y)
                # pydirectinput.click(x, y, duration=0.025)
                ctypes.windll.user32.SetCursorPos(x, y)
                ctypes.windll.user32.mouse_event(
                    0x0002, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(
                    0x0004, 0, 0, 0, 0)
            elif button == "Button.right":
                xrat, yrat = direction.split("|")
                x, y = BotUtils.convert_window_to_true(self.gamename,
                                                       float(xrat), float(yrat))
                x = int(x)
                y = int(y)
                ctypes.windll.user32.SetCursorPos(x, y)
                ctypes.windll.user32.mouse_event(
                    0x0008, 0, 0, 0, 0)
                time.sleep(0.03)
                ctypes.windll.user32.mouse_event(
                    0x00010, 0, 0, 0, 0)
            elif button == "quit":
                print("Shutting down server")
                os._exit(1)
            elif button == "'x'":
                if self.allowx:
                    if direction == "down":
                        if self.inputmode:
                            pydirectinput.keyDown("x")
                        else:
                            CustomInput.press_key(CustomInput.key_map["x"])
                    else:
                        if self.inputmode:
                            pydirectinput.keyUp("x")
                        else:
                            CustomInput.release_key(CustomInput.key_map["x"])
                elif direction == "down":
                    self.loot_if_available()
                else:
                    if self.inputmode:
                        pydirectinput.keyUp("x")
                    else:
                        CustomInput.release_key(CustomInput.key_map["x"])
            elif button == "regroup":
                self.regroup(direction)
            elif button == "autoloot":
                if direction == "on":
                    self.autoloot_thread_start()
                else:
                    self.autoloot_enabled = False
            elif button == "inputmode":
                if direction == "1":
                    self.inputmode = True
                else:
                    self.inputmode = False
            elif button == "questhandle":
                self.quest_handle.start_quest_handle()
            elif button == "batch":
                self.batch_handle(direction)
            elif button == "clearall":
                BotUtils.close_map_and_menu(self.gamename)
            elif button == "sellrepair":
                self.sell_repair.ident_sell_repair()
            elif button == "follow":
                if direction == "1":
                    self.followmode = True
                    self.create_follower_thread()
                    if self.support:
                        self.create_support_thread()
                else:
                    self.followmode = False
            elif button == "follow":
                if direction == "1":
                    self.support = True
                    if self.followmode:
                        self.create_support_thread()
                else:
                    self.support = False
            elif button == "xallow":
                if direction == "1":
                    self.allowx = True
                else:
                    self.allowx = False
            elif direction == "down":
                key = BotUtils.convert_pynput_to_pag(
                    button.replace("'", ""))
                if self.move_only:
                    if button in self.move_only_exclude_keys:
                        if self.inputmode:
                            pydirectinput.keyDown(key)
                        else:
                            CustomInput.press_key(
                                CustomInput.key_map[key], key)
                else:
                    if self.inputmode:
                        pydirectinput.keyDown(key)
                    else:
                        CustomInput.press_key(CustomInput.key_map[key], key)
            elif direction == "up":
                key = BotUtils.convert_pynput_to_pag(
                    button.replace("'", ""))
                if self.move_only:
                    if button in self.move_only_exclude_keys:
                        if self.inputmode:
                            pydirectinput.keyUp(key)
                        else:
                            CustomInput.release_key(
                                CustomInput.key_map[key], key)
                else:
                    if self.inputmode:
                        pydirectinput.keyUp(key)
                    else:
                        CustomInput.release_key(CustomInput.key_map[key], key)

    def pre_regroup_updates(self, x, y):
        self.level_name = BotUtils.detect_level_name(self.gamename)
        # Then grab the right rect for the level
        try:
            self.map_rect = BotUtils.string_to_rect(
                self.rects[self.level_name])
            self.speed = self.speeds[self.level_name]
        except:
            try:
                best_match = process.extractOne(
                    self.level_name, self.rects, score_cutoff=0.8)
                self.map_rect = BotUtils.string_to_rect(
                    self.rects[best_match])
                self.speed = self.speeds[best_match]
            except:
                self.map_rect = [362, 243, 1105, 748]
                self.speed = 30
        # Then open the map
        if not BotUtils.detect_bigmap_open():
            BotUtils.try_toggle_map()
        self.player_pos = BotUtils.grab_player_pos(
            self.gamename, [x-100, y-100, x+100, y+100])

    def regroup(self, coords: str):
        x, y = coords.split("|")
        # first perform the pre-regroup updates
        self.pre_regroup_updates(int(x), int(y))
        # Then calculate the relative positions
        try:
            relx = self.player_pos[0] - int(x)
            rely = int(y) - self.player_pos[1]
            BotUtils.move_diagonal(self.gamename, relx,
                                   rely, 90, self.speed, True)
        except:
            if self.regroup_try_count < 2:
                self.regroup_try_count += 1
                key = "right"
                CustomInput.press_key(CustomInput.key_map[key])
                CustomInput.release_key(CustomInput.key_map[key])
                self.regroup(coords)
        self.player_pos = [0, 0]
        self.regroup_try_count = 0

    def create_follower_thread(self):
        t = threading.Thread(target=self.follower)
        t.start()

    def follower(self):
        dung_cap = WindowCapture(self.gamename, [1090, 331, 1092, 353])
        detect_count = 0
        while self.followmode:
            if Events.detect_in_dungeon(dung_cap):
                loc = BotUtils.find_other_player(self.gamename)
                if loc:
                    playerx, playery = BotUtils.grab_player_pos(
                        self.gamename, [1100, 50, 1260, 210], True)
                    if playerx:
                        relx = loc[0] - playerx
                        rely = playery - loc[1]
                        self.follower.navigate_towards(relx, rely)
                        detect_count += 1
                elif detect_count > 0:
                    detect_count -= 1
                else:
                    BotUtils.stop_movement(self.follower)
            time.sleep(0.005)
        BotUtils.stop_movement(self.follower)

    def create_support_thread(self):
        t = threading.Thread(target=self.support_MS)
        t.start()

    def support_MS(self):
        dung_cap = WindowCapture(self.gamename, [1090, 331, 1092, 353])
        while self.followmode and self.support:
            if Events.detect_in_dungeon(dung_cap):
                if BotUtils.find_enemy(self.gamename):
                    for key in ["s", "a", "f", "h"]:
                        CustomInput.press_key(CustomInput.key_map[key])
                        CustomInput.release_key(CustomInput.key_map[key])
            time.sleep(0.005)

    def create_revive_thread(self):
        t = threading.Thread(target=self.auto_revive)
        t.start()

    def auto_revive(self):
        dung_cap = WindowCapture(self.gamename, [1090, 331, 1092, 353])
        while True:
            try:
                if Events.detect_in_dungeon(dung_cap):
                    if Events.detect_resurrect_prompt(self.gamename):
                        CustomInput.press_key(CustomInput.key_map["x"])
                        CustomInput.release_key(CustomInput.key_map["x"])
            except:
                time.sleep(2)


if __name__ == "__main__":
    lst = RHBotArrayServer(print_only=False)
    lst.start()
