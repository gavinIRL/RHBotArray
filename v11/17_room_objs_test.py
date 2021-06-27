# This file will test how to best store data on each room
# Will preferably load information from a single file
import os


class Room():
    def __init__(self, line: str) -> None:
        # Format of each line in the file should be as follows
        # coords_n | coords_n+1 # action_n | action_n+1 # tags
        # format coords is x,y
        # ------------------------------------
        # list actions is as follows:
        # clear,l - position to perform clear from, point left (r,u,d)
        # boss,l - position to perform boss attacks from (r,u,d)
        # exit - position to exit room from
        # chest,l - position to attack chest, point left (r,u,d)
        # repos,l,5 - position to reposition to, point left, after seconds (r,u,d)
        # loot - position to attempt to loot from
        # wypt - this is a travel waypoint only
        # ------------------------------------
        # list of tags is as follows
        # nxtbss,l - next room is the boss room, hold l to enter (r,u,d)
        # curbss - this room is the boss room
        # nocmbt - this room is just for walking through
        coords, actions, tags = line.split("#")
        self.action_list = []
        self.coord_list = []
        self.tags = []
        for coord in coords.split("|"):
            x, y = coord.split(",")
            self.coord_list.append((int(x), int(y)))
        for action in actions.split("|"):
            self.action_list.append(action)
        for tag in tags.split("|"):
            self.tags.append(tag)


class RoomTest():
    dir_list = ["l", "r", "u", "d"]

    def room_handler(self, room: Room):
        # Check through the tags first
        nocmbt = False if not "nocmbt" in "".join(room.tags) else True
        curbss = False if not "curbss" in "".join(room.tags) else True
        nxtbss = False if not "nxtbss" in "".join(room.tags) else True
        repos = False if not "repos" in "".join(room.action_list) else True
        # Then go through the actions and carry them out
        for i, action in enumerate(room.action_list):
            coords = room.coord_list[i]
            if "clear" in action:
                pass
            elif "boss" in action:
                pass
            elif "exit" in action:
                pass
            elif "chest" in action:
                pass
            elif "repos" in action:
                pass
            elif "loot" in action:
                pass
            elif "wypt" in action:
                pass

    def perform_clear(self, coords, dir, repos=False):
        pass

    def perform_boss(self, coords, dir, repos=False):
        pass

    def perform_exit(self, coords, nxtbss=False):
        pass

    def perform_chest(self, coords, dir):
        pass

    def perform_repos(self, coords, dir):
        pass

    def perform_loot(self, coords, currbss=False):
        pass

    def perform_wypt(self, coords):
        pass


def load_rooms(filename):
    with open(filename) as f:
        lines = f.readlines()
    list_rooms = []
    for line in lines:
        list_rooms.append(Room(line))
    return list_rooms


filename = os.path.dirname(
    os.path.abspath(__file__)) + "/levels/map10updated.txt"
rooms = load_rooms(filename)
room1 = rooms[0]
print(room1.action_list)
