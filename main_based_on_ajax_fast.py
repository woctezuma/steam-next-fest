import asyncio
import datetime
import json

import websockets

from src.asf_utils import process_appids
from src.data_utils import (
    load_event_apps,
)
from src.data_utils import (
    load_known_apps,
    load_demos,
    load_unfiltered_demos,
    load_event_demos,
    load_owned_apps,
)
from src.scheduler_utils import AjaxScheduler, SteamScheduler, update_cache_of_ids_to_monitor


def load_monitored_ids():
    event_demos = set(load_event_demos())
    unfiltered_demo_ids = set(load_unfiltered_demos())
    relevant_app_ids = set(load_demos())  # not actually demos, just relevant unowned apps

    monitored_ids = event_demos | unfiltered_demo_ids | relevant_app_ids

    return monitored_ids


def has_event_game(appids, event_app_ids):
    return not set(appids).isdisjoint(event_app_ids)


def has_unknown_app(appids, excluded_ids):
    return not set(appids).issubset(excluded_ids)


async def handler(websocket):
    resume_afterwards = False
    verbose = True
    ajax_scheduler = AjaxScheduler(cooldown_in_sec=180, verbose=verbose)
    steam_scheduler = SteamScheduler(cooldown_in_sec=1800, verbose=verbose)

    monitored_ids = set(load_monitored_ids())
    event_ids = set(load_event_apps())
    known_ids = set(load_known_apps())
    owned_ids = set(load_owned_apps())

    if verbose:
        print(f"#monitored_apps = {len(monitored_ids)}")
        print(f"#event_games = {len(event_ids)}")
        print(f"#excluded_apps = {len(known_ids)}")
        print(f"#owned_apps = {len(owned_ids)}")

    current_time = datetime.datetime.now()
    print(f"Connected to the WebSocket at {current_time}")

    while True:
        message = await websocket.recv()
        data = json.loads(message)

        if "Apps" in data:
            appids = {int(app_id) for app_id in data["Apps"]}

            if len(appids) == 0:
                continue

            if verbose:
                try:
                    change_number = data["ChangeNumber"]
                except KeyError:
                    change_number = None
                current_time = datetime.datetime.now()
                print(f"[{current_time}] change n°{change_number} 👀 {appids}")

            detected_appids = appids & monitored_ids

            if len(detected_appids) > 0:
                await process_appids(
                    detected_appids, owned_ids, resume_afterwards=resume_afterwards, keyword="monitored",
                    verbose=verbose
                )

            if has_event_game(appids, event_ids) or has_unknown_app(appids, known_ids):
                # The order is important: first, AJAX ; then, Steam.
                new_ajax_ids, _ = ajax_scheduler.update()
                new_steam_ids, has_updated_steam_cache = steam_scheduler.update()

                new_demo_ids = set(new_ajax_ids).union(new_steam_ids)

                if len(new_demo_ids) > 0:
                    await process_appids(
                        new_demo_ids, owned_ids, resume_afterwards=resume_afterwards, keyword="updated", verbose=verbose
                    )
                    monitored_ids |= new_demo_ids

                if has_updated_steam_cache:
                    unowned_demos, relevant_ids, known_ids = update_cache_of_ids_to_monitor()
                    monitored_ids |= unowned_demos | relevant_ids


async def main():
    url = "ws://localhost:8181"
    async with websockets.connect(url) as ws:
        await handler(ws)
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
