import numpy as np  # type: ignore

from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, map_width: int, map_height: int, view_width: int, view_height: int,
                 player_x: int, player_y: int):
        self.map_width, self.map_height = map_width, map_height
        self.view_width, self.view_height = view_width, view_height
        self.viewport_origin_x = int(player_x - self.view_width/2)
        self.viewport_origin_y = int(player_y - self.view_height/2 + 1)
        # ^The +1 is sort of a hack fix for issues that arise from the division when defining the viewport origin based
        # on the player position.
        """
        The following buffer code is a temporary implementation to prevent the out-of-bounds viewport errors
        until I find a more elegant way to fix it. Might be better to implement something in the in_bounds function.
        """
        self.buffer_x = int(view_width/2)
        self.buffer_y = int(view_height/2)
        self.map_tiles = np.full((map_width + 2*self.buffer_x, map_height + 2*self.buffer_y), fill_value=tile_types.floor,
                                 order="F")

        #  Walling off the buffer zone so the player can't stray.....
        # self.map_tiles[self.buffer_x:self.buffer_x+self.map_width, self.buffer_y] = tile_types.wall
        # self.map_tiles[self.buffer_x:self.buffer_x+self.map_width, self.buffer_y+self.map_height] = tile_types.wall
        # self.map_tiles[self.buffer_x, self.buffer_y:self.buffer_y + self.map_height] = tile_types.wall
        # self.map_tiles[self.buffer_x+self.map_width, self.buffer_y:self.buffer_y + self.map_height] = tile_types.wall

        # Temp wall:
        self.map_tiles[self.buffer_x+60:self.buffer_x+100, self.buffer_y+22] = tile_types.wall

        #  This will probably break pretty quickly. Also, apparently this is a numpy "view" not "copy",
        #  which is something to keep in mind..
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
