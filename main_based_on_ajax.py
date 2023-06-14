import asyncio
import datetime
import json

import websockets

from src.asf_utils import add_and_play
from src.data_utils import (
    load_event_apps,
)
from src.data_utils import load_known_apps, load_demos, load_unfiltered_demos, load_event_demos
from src.scheduler_utils import AjaxScheduler, SteamScheduler, update_cache_of_ids_to_monitor


def load_monitored_ids():
    relevant_app_ids = load_demos()  # not actually demos, just relevant unowned apps
    unfiltered_demo_ids = load_unfiltered_demos()
    event_demos = load_event_demos()

    monitored_ids = set(relevant_app_ids + unfiltered_demo_ids + event_demos)

    return monitored_ids


async def handler(websocket):
    verbose = True
    very_verbose = False

    ajax_scheduler = AjaxScheduler(cooldown_in_sec=0.5, verbose=verbose)
    steam_scheduler = SteamScheduler(cooldown_in_sec=1200, verbose=verbose)

    # TODO make sure you have called run_ajax_queries.py and that the data/event*.txt files are well populated!
    # TODO make sure that you have then called find_missing_demos_in_ISteamApps.py to be as exhaustive as possible!
    monitored_ids = load_monitored_ids()
    event_app_ids = load_event_apps()
    excluded_ids = load_known_apps()

    if verbose:
        print(f"Connected to the WebSocket at {datetime.datetime.now()}")

    while True:
        message = await websocket.recv()
        data = json.loads(message)
        if "Apps" in data:
            appids = set(int(id) for id in data["Apps"])

            if len(appids) == 0:
                continue

            if very_verbose:
                try:
                    change_number = data["ChangeNumber"]
                except KeyError:
                    change_number = None
                print(f"[{datetime.datetime.now()}] change n°{change_number} 👀 {appids}")

            # Compare to monitored demo ids
            detected_appids = appids.intersection(monitored_ids)

            if len(detected_appids) > 0:
                await add_and_play(list(detected_appids))
                if verbose:
                    current_time = datetime.datetime.now()
                    print(f"[{current_time}] -> ASF 👌 {detected_appids}")

            # Compare to event game ids
            detected_game_ids = appids.intersection(event_app_ids)

            # Check if there are unknown apps
            unknown_app_ids = appids.difference(excluded_ids)

            if len(detected_game_ids) > 0 or len(unknown_app_ids) > 0:
                # FIRST APPROACH USING AJAX. NB: these demos ALL take part in Steam Next Fest!
                new_demo_ids, has_performed_ajax_update = ajax_scheduler.update()

                if len(new_demo_ids) > 0:
                    monitored_ids = monitored_ids.union(new_demo_ids)

                    await add_and_play(list(new_demo_ids))
                    if verbose:
                        current_time = datetime.datetime.now()
                        print(f"[{current_time}] -> ASF/AJAX 👌 {new_demo_ids}")

                # SECOND APPROACH USING ISTEAMAPPS. Caveat: these demos could be ANYTHING!
                new_demo_ids, has_updated_steam_cache = steam_scheduler.update()

                if has_updated_steam_cache:
                    unowned_demos, relevant_ids, known_ids = update_cache_of_ids_to_monitor()
                    monitored_ids = load_monitored_ids()
                    excluded_ids = load_known_apps()

                    if len(new_demo_ids) > 0:
                        monitored_ids = monitored_ids.union(new_demo_ids)

                        # Compare to newly monitored demo ids
                        detected_appids = appids.intersection(new_demo_ids)

                        if len(detected_appids) > 0:
                            await add_and_play(list(detected_appids))
                            if verbose:
                                current_time = datetime.datetime.now()
                                print(f"[{current_time}] -> ASF/ISteamApps 👌 {detected_appids}")


async def main():
    url = "ws://localhost:8181"
    async with websockets.connect(url) as ws:
        await handler(ws)
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
