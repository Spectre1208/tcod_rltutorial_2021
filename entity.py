from __future__ import annotations

import copy
from typing import Tuple, TypeVar, TYPE_CHECKING, Optional, Type

from render_order import RenderOrder

if TYPE_CHECKING:
    from game_map import GameMap
    from components.ai import BaseAI
    from components.fighter import Fighter

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    game_map: GameMap

    def __init__(
            self,
            game_map: Optional[GameMap] = None,
            map_x: int = 0,
            map_y: int = 0,
            char: str = "?",
            color: Tuple[int, int, int] = (255, 255, 255),
            name: str = "<Unnamed>",
            blocks_movement: bool = False,
            render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.map_x = map_x
        self.map_y = map_y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if game_map:
            # If game_map isn't provided now then it will be set later.
            self.game_map = game_map
            game_map.entities.add(self)

    def spawn(self: T, game_map: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the give location."""
        clone = copy.deepcopy(self)
        clone.map_x = x
        clone.map_y = y
        clone.game_map = game_map
        game_map.entities.add(clone)
        return clone

    def place(self, x: int, y: int, game_map: Optional[GameMap] = None) -> None:
        """Place this entity at a new location. Handles moving across GameMaps."""
        self.map_x = x
        self.map_y = y
        if game_map:
            if hasattr(self, "game_map"):  # Possibly uninitialized.
                self.game_map.entities.remove(self)
            self.game_map = game_map
            game_map.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.map_x += dx
        self.map_y += dy

class Actor(Entity):
    def __init__(
            self,
            *,
            x: int = 0,
            y: int = 0,
            char: str = "?",
            color: Tuple[int, int, int] = (255, 255, 255),
            name: str = "<Unnamed>",
            ai_cls: Type[BaseAI],
            fighter: Fighter
    ):
        super().__init__(
            map_x=x,
            map_y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.fighter = fighter
        self.fighter.entity = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)
