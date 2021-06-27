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
        # repos,l - position to reposition to, point left (r,u,d)
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
            if "nxtbss" in tag:
                _, dir = tag.split(",")
            self.tags.append(tag)


class RoomTest():
    dir_list = ["l", "r", "u", "d"]

    def room_handler(self, room: Room):
        # Check through the tags first
        nocmbt = False if not "nocmbt" in "".join(room.tags) else True
        curbss = False if not "curbss" in "".join(room.tags) else True
        nxtbss = False if not "nxtbss" in "".join(room.tags) else True


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
