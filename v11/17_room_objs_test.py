# This file will test how to best store data on each room
# Will preferably load information from a single file


class Room():
    def __init__(self, file) -> None:
        # Format of each line in the file should be as follows
        # actiontype | presleep | postsleep | list-of-coords
        with open(file) as f:
            lines = f.readlines()
