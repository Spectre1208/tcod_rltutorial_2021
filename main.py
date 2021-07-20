#!/usr/bin/env python3
import tcod

from engine import Engine
from entity import Entity
from input_handlers import EventHandler
from procgen import generate_dungeon


def main() -> None:
    screen_columns = 80
    screen_rows = 50
    screen_width = int(screen_columns*10*1.5)
    screen_height = int(screen_rows*10*1.5)

    map_width = 80
    map_height = 45

    view_width = 80
    view_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()
    player_color = (255, 255, 255)
    npc_color = (255, 255, 0)
    player = Entity(int(map_width / 2), int(map_height / 2), "@", player_color, isplayer=True)
    npc = Entity(int(map_width / 2 - 5), int(map_height / 2), "N", npc_color)
    npc_2 = Entity(int(map_width / 2 + 50), int(map_height / 2 + 50), "N", npc_color)
    entities = {npc, npc_2, player}

    game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        view_width=view_width,
        view_height=view_height,
        player=player
    )

    engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map, player=player)

    with tcod.context.new(
        width=screen_width,
        height=screen_height,
        tileset=tileset,
        title="Roguelike Tutorial 2021",
        vsync=True
    ) as context:
        root_console = tcod.Console(screen_columns, screen_rows, order="F")
        while True:
            engine.render(console=root_console, context=context)

            events = tcod.event.wait()

            engine.handle_events(events)


if __name__ == "__main__":
    main()
