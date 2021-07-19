from typing import Tuple


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, map_x: int, map_y: int, char: str, color: Tuple[int, int, int], isplayer=False):
        self.map_x = map_x
        self.map_y = map_y
        self.char = char
        self.color = color
        self.isplayer = isplayer
        # ^This was added to assist in viewport calculations. The renderer currently
        # renders the player differently from other entities due to the viewport moving with it.

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.map_x += dx
        self.map_y += dy
