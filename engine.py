from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console

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

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player, self.game_map)

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        """
        The following calculates the viewport coordinates for each entity, checks to make sure that
        the coordinates are actually within the current viewport, and then prints them to the viewport.
        For now, the player entity is excluded from this and is printed to the center of the viewport at 
        all times.
        """
        for entity in self.entities:
            # if entity.isplayer:
            #     player_x = int(self.game_map.view_width/2)
            #     player_y = int(self.game_map.view_height/2)
            #     console.print(player_x, player_y, entity.char, fg=entity.color)
            # else:
            view_x = entity.map_x - self.game_map.viewport_origin_x
            view_y = entity.map_y - self.game_map.viewport_origin_y
            if (0 <= view_x < self.game_map.view_width) and (0 <= view_y < self.game_map.view_height):
                console.print(view_x, view_y, entity.char, fg=entity.color)

        context.present(console)

        console.clear()
