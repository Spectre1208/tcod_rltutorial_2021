from __future__ import annotations

from typing import Iterable, Optional, TYPE_CHECKING, Iterator

import numpy as np  # type: ignore

from tcod.console import Console

from entity import Actor
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
            self, engine: Engine, map_width: int, map_height: int, view_width: int, view_height: int,
            entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.entities = set(entities)
        """
        The following buffer code is a temporary implementation to prevent the out-of-bounds viewport errors
        until I find a more elegant way to fix it. Might be better to implement something in the in_bounds function.
        """
        self.buffer_x = int(view_width/2)
        self.buffer_y = int(view_height/2)
        # Adding view width and height to map width and height to create the buffer zone of the right size.
        self.map_width = map_width + view_width
        self.map_height = map_height + view_height
        self.view_width, self.view_height = view_width, view_height
        # Initialize the viewport at the center of the map. This will be overridden later.
        self.viewport_origin_x = int(map_width / 2 - self.view_width / 2)
        self.viewport_origin_y = int(map_height / 2 - self.view_height / 2 + 1)
        # ^The +1 is sort of a hack fix for issues that arise from the division when defining the viewport origin based
        # on the player position.
        self.map_tiles = np.full((self.map_width, self.map_height), fill_value=tile_types.wall, order="F")

        #  Current viewport implementation. Keep in mind that this is a "view" and not a "copy" of the tiles array:
        self.viewport_tiles = self.map_tiles[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                             self.viewport_origin_y:self.viewport_origin_y + self.view_height]

        self.visible = np.full(
            (self.map_width, self.map_height), fill_value=False, order="F"
        )  # Tiles the player can currently see

        self.explored = np.full(
            (self.map_width, self.map_height), fill_value=False, order="F"
        )  # Tiles the player has seen before

        """
        For now, creating separate "viewports" for the visible and explored matrices. It would be nice to add this to
        the tile metadata.. but I'll go down that road later. 
        """
        self.visible_vp = self.visible[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                       self.viewport_origin_y:self.viewport_origin_y + self.view_height]
        self.explored_vp = self.explored[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                         self.viewport_origin_y:self.viewport_origin_y + self.view_height]

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this map's living actors"""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    def focus_viewport(self, player_x: int, player_y: int):
        """Recalculates viewport origin based on new player coordinates. Maybe I should just call this
        whenever MovementActions are performed?"""
        self.viewport_origin_x = int(player_x - self.view_width / 2)
        self.viewport_origin_y = int(player_y - self.view_height / 2 + 1)
        self.viewport_tiles = self.map_tiles[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                             self.viewport_origin_y:self.viewport_origin_y + self.view_height]
        self.visible_vp = self.visible[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                       self.viewport_origin_y:self.viewport_origin_y + self.view_height]
        self.explored_vp = self.explored[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                         self.viewport_origin_y:self.viewport_origin_y + self.view_height]

    def get_blocking_entity_at_location(self, location_x: int, location_y: int) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.map_x == location_x
                and entity.map_y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.map_x == x and actor.map_y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:  # This is broken
        """Return True if x and y are inside of the bounds of the map."""
        return self.buffer_x <= x < self.buffer_x + self.map_width and self.buffer_y <= y < self.buffer_y + \
               self.map_height

    def scroll_viewport(self, dx: int, dy: int) -> None:
        """
        Defines a new viewport origin using the movement dx and dy variables and updates
        the viewport with the new origin.

        Also updates the FOV viewport matrices.
        """
        self.viewport_origin_x += dx
        self.viewport_origin_y += dy
        self.viewport_tiles = self.map_tiles[self.viewport_origin_x:self.viewport_origin_x+self.view_width,
                                             self.viewport_origin_y:self.viewport_origin_y+self.view_height]
        self.visible_vp = self.visible[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                       self.viewport_origin_y:self.viewport_origin_y + self.view_height]
        self.explored_vp = self.explored[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                         self.viewport_origin_y:self.viewport_origin_y + self.view_height]

    def render(self, console: Console) -> None:
        # console.tiles_rgb[0:self.view_width, 0:self.view_height] = self.viewport_tiles["dark"]
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.tiles_rgb[0 : self.view_width, 0 : self.view_height] = np.select(
            condlist=[self.visible_vp, self.explored_vp],
            choicelist=[self.viewport_tiles["light"], self.viewport_tiles["dark"]],
            default=tile_types.SHROUD
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        """
        The following calculates the viewport coordinates for each entity, checks to make sure that
        the coordinates are actually within the current viewport, and then prints them to the viewport.
        
        """
        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV.
            if self.visible[entity.map_x, entity.map_y]:
                view_x = entity.map_x - self.viewport_origin_x
                view_y = entity.map_y - self.viewport_origin_y
                if (0 <= view_x < self.view_width) and (0 <= view_y < self.view_height):
                    console.print(x=view_x, y=view_y, string=entity.char, fg=entity.color)
