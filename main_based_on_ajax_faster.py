import asyncio
import datetime
import json
import time

import websockets

from main_based_on_ajax_fast import load_monitored_ids, load_owned_apps
from run_ajax_queries import perform_incremental_update_of_event_files
from src.asf_utils import add_and_play
from src.data_utils import load_demos_already_counted, load_known_apps


async def handler(websocket):
    resume_afterwards = False

    known_ids = set(load_known_apps())

    print(f"[{datetime.datetime.now()}] Connected to the WebSocket")

    monitored_ids = set(load_monitored_ids())
    print(f'#monitored_ids (all) = {len(monitored_ids)}')

    owned_ids = set(load_owned_apps())
    already_counted_ids = set(load_demos_already_counted())

    skipped_ids = owned_ids & already_counted_ids
    print(f'#ids (skipped) = {len(skipped_ids)}')

    monitored_ids -= skipped_ids
    print(f'#monitored_ids (filtered) = {len(monitored_ids)}')

    ajax_cooldown_in_sec = 360
    ajax_last_updated = None

    dummy_appids = [1937340]
    asf_cooldown_in_sec = 300  # careful with rate-limits due to the fake addlicense!
    asf_last_updated = None

    while True:
        message = await websocket.recv()
        data = json.loads(message)

        if "Apps" in data:
            if ajax_last_updated is None or (time.time() - ajax_last_updated) > ajax_cooldown_in_sec:
                ajax_start_time = datetime.datetime.now()
                new_demo_ids = perform_incremental_update_of_event_files()
                ajax_last_updated = time.time()
                if len(new_demo_ids) > 0:
                    monitored_ids |= set(new_demo_ids)
                print(f"[{ajax_start_time}] -> [{datetime.datetime.now()}] AJAX update")

            appids = {int(app_id) for app_id in data["Apps"]}
            detected_appids = appids & monitored_ids

            if len(detected_appids) > 0:
                asf_start_time = datetime.datetime.now()
                await add_and_play(list(detected_appids),
                                   resume_afterwards=resume_afterwards)
                asf_last_updated = time.time()  # Right after any call to add_and_play()
                print(f"[{asf_start_time}] -> [{datetime.datetime.now()}] ASF {detected_appids}")

            # TODO check ASF code for:
            # - resume/reset/pause
            #   Reference: https://github.com/JustArchiNET/ArchiSteamFarm/issues/662#issuecomment-333344800
            # - addlicense/PICS
            #   - app:  SteamApps.RequestFreeLicense
            #           -> https://github.com/JustArchiNET/ArchiSteamFarm/blob/c67aecacbc96c8bd6c022fa28863ef7597f0761a/ArchiSteamFarm/Steam/Interaction/Commands.cs#L655
            #           -> https://github.com/SteamRE/SteamKit/blob/40757b72a428ca1d98619e3131041c079dbf2618/SteamKit2/SteamKit2/Steam/Handlers/SteamApps/SteamApps.cs#L277
            #   - sub: ArchiWebHandler.AddFreeLicense
            #           -> not used

            # TODO time ASF for addlicense app/
            # TODO try to use Steam Python package to get app info so that I can addlicense sub/ (faster) instead?

            detected_unknown_appids = appids - known_ids
            if len(detected_unknown_appids) > 0:
                dummy_appids = detected_unknown_appids

            force_asf_update = bool(asf_last_updated is None or (time.time() - asf_last_updated) > asf_cooldown_in_sec)

            if force_asf_update:
                # Caveat: "ASF will use Steam network activation for apps"
                # Reference: https://github.com/JustArchiNET/ArchiSteamFarm/wiki/Commands#addlicense-licenses
                asf_start_time = datetime.datetime.now()
                await add_and_play(dummy_appids,
                                   resume_afterwards=resume_afterwards)
                asf_last_updated = time.time()  # Right after any call to add_and_play()
                print(f"[{asf_start_time}] -> [{datetime.datetime.now()}] ASF/updated")


async def main():
    url = "ws://localhost:8181"
    async with websockets.connect(url) as ws:
        await handler(ws)
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
