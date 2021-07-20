from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from actions import EscapeAction, MovementAction
from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler


class Engine:
    def __init__(self, entities: Set[Entity], event_handler: EventHandler, game_map: GameMap, player: Entity):
        self.entities = entities
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.update_fov()

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player, self.game_map)

            self.update_fov()  # Update the FOV before the player's next action.

    def update_fov(self) -> None:
        """Recompute the visible area based on the player's point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.map_tiles["transparent"],
            (self.player.map_x, self.player.map_y),
            radius=8
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        """
        The following calculates the viewport coordinates for each entity, checks to make sure that
        the coordinates are actually within the current viewport, and then prints them to the viewport.
        For now, the player entity is excluded from this and is printed to the center of the viewport at 
        all times.
        """
        for entity in self.entities:
            # Only print entities that are in the FOV.
            if self.game_map.visible[entity.map_x, entity.map_y]:
                view_x = entity.map_x - self.game_map.viewport_origin_x
                view_y = entity.map_y - self.game_map.viewport_origin_y
                if (0 <= view_x < self.game_map.view_width) and (0 <= view_y < self.game_map.view_height):
                    console.print(view_x, view_y, entity.char, fg=entity.color)

        context.present(console)

        console.clear()
