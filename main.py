import asyncio
import json
import math

import gevent
import websockets
from steam.client import SteamClient

from src.asf_utils import add_and_play
from src.data_utils import load_demos, load_unfiltered_demos, load_known_apps


async def handler(websocket, monitored_ids, excluded_ids, heuristic_range=None):
    timeout = 1

    while True:
        message = await websocket.recv()
        print(message)
        data = json.loads(message)
        if "Apps" in data:
            appids = [int(id) for id in data["Apps"]]

            detected_appids = list(set(appids).intersection(monitored_ids))
            if len(detected_appids) > 0:
                await add_and_play(list(detected_appids))

            unknown_app_ids = list(set(appids).difference(excluded_ids))
            if heuristic_range is not None:
                num_digits = math.ceil(math.log10(max(heuristic_range)))
                unknown_app_ids = [
                    int(id)
                    for id in unknown_app_ids
                    if heuristic_range[0]
                       <= int(str(id)[:num_digits])
                       <= heuristic_range[1]
                ]
            if len(unknown_app_ids) > 0:
                try:
                    steam_client = SteamClient()
                    steam_client.anonymous_login()
                    out = steam_client.get_product_info(
                        apps=unknown_app_ids, timeout=timeout
                    )
                    steam_client.logout()
                except gevent.timeout.Timeout:
                    print(f"Timeout for {unknown_app_ids}")
                    out = {"apps": {}}

                unknown_app_ids_to_try = []
                for app in out["apps"].values():
                    print(app)
                    try:
                        app_id = int(app["appid"])
                        app_type = app["common"]["type"]
                        app_release_state = app["common"]["releasestate"]
                    except KeyError:
                        print("KeyError")
                        continue

                    if app_type == "Demo" and app_release_state == "released":
                        print("Queued demo!")
                        unknown_app_ids_to_try.append(app_id)
                    else:
                        print(f"Dropped app : {app_type} / {app_release_state}")

                if len(unknown_app_ids_to_try) > 0:
                    await add_and_play(list(unknown_app_ids_to_try))


async def main():
    relevant_app_ids = load_demos()  # not actually demos, just relevant unowned apps
    unfiltered_demo_ids = load_unfiltered_demos()
    monitored_ids = set(relevant_app_ids + unfiltered_demo_ids)

    known_app_ids = load_known_apps()

    # TODO: heuristic to decrease the number of Steam API calls to try to avoid time-outs.
    heuristic_range = [
        170,
        206,
    ]

    url = "ws://localhost:8181"
    async with websockets.connect(url) as ws:
        await handler(
            ws,
            monitored_ids=monitored_ids,
            excluded_ids=known_app_ids,
            heuristic_range=heuristic_range,
        )
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
