import numpy as np  # type: ignore

from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, map_width: int, map_height: int, view_width: int, view_height: int):
        self.map_width, self.map_height = map_width, map_height
        self.view_width, self.view_height = view_width, view_height
        # Initialize the viewport at the center of the map. This will be overridden later.
        self.viewport_origin_x = int(map_width/2 - self.view_width/2)
        self.viewport_origin_y = int(map_height/2 - self.view_height/2 + 1)
        # ^The +1 is sort of a hack fix for issues that arise from the division when defining the viewport origin based
        # on the player position.
        """
        The following buffer code is a temporary implementation to prevent the out-of-bounds viewport errors
        until I find a more elegant way to fix it. Might be better to implement something in the in_bounds function.
        """
        self.buffer_x = int(view_width/2)
        self.buffer_y = int(view_height/2)
        self.map_tiles = np.full((map_width + view_width, map_height + view_height),
                                 fill_value=tile_types.wall, order="F")

        #  Current viewport implementation. Keep in mind that this is a "view" and not a "copy":
        self.viewport_tiles = self.map_tiles[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                             self.viewport_origin_y:self.viewport_origin_y + self.view_height]

    def focus_viewport(self, player_x: int, player_y: int):
        """Recalculates viewport origin based on new player coordinates. Maybe I should just call this
        whenever MovementActions are performed?"""
        self.viewport_origin_x = int(player_x - self.view_width / 2)
        self.viewport_origin_y = int(player_y - self.view_height / 2 + 1)
        self.viewport_tiles = self.map_tiles[self.viewport_origin_x:self.viewport_origin_x + self.view_width,
                                             self.viewport_origin_y:self.viewport_origin_y + self.view_height]

    def in_bounds(self, x: int, y: int) -> bool:  # This is broken
        """Return True if x and y are inside of the bounds of the map."""
        return self.buffer_x <= x < self.buffer_x + self.map_width and self.buffer_y <= y < self.buffer_y + \
               self.map_height

    def scroll_viewport(self, dx: int, dy: int) -> None:
        """
        Defines a new viewport origin using the movement dx and dy variables and updates
        the viewport with the new origin.
        """
        self.viewport_origin_x += dx
        self.viewport_origin_y += dy
        self.viewport_tiles = self.map_tiles[self.viewport_origin_x:self.viewport_origin_x+self.view_width,
                                             self.viewport_origin_y:self.viewport_origin_y+self.view_height]

    def render(self, console: Console) -> None:
        console.tiles_rgb[0:self.view_width, 0:self.view_height] = self.viewport_tiles["dark"]
