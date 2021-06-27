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
        # clearl - position to perform clear from, point left (r,u,d)
        # bossl - position to perform boss attacks from (r,u,d)
        # exit - position to exit room from
        # chestl - position to attack chest, point left (r,u,d)
        # reposl - position to reposition to, point left (r,u,d)
        # loot - position to attempt to loot from
        # wypt - this is a travel waypoint only
        # ------------------------------------
        # list of tags is as follows
        # nxtbssl - next room is the boss room, hold l to enter (r,u,d)
        # curbss - this room is the boss room
        # nocmbt - this room is just for walking through
        coords, actions, tags = line.split("#")
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
