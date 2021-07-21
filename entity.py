from __future__ import annotations

import copy
from typing import Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(
            self,
            map_x: int = 0,
            map_y: int = 0,
            char: str = "?",
            color: Tuple[int, int, int] = (255, 255, 255),
            name: str = "<Unnamed>",
            blocks_movement: bool = False,
    ):
        self.map_x = map_x
        self.map_y = map_y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    def spawn(self: T, game_map: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the give location."""
        clone = copy.deepcopy(self)
        clone.map_x = x
        clone.map_y = y
        game_map.entities.add(clone)
        return clone

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.map_x += dx
        self.map_y += dy
