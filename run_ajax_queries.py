import datetime

import requests

from src.data_utils import get_fname_for_participating_demos_based_on_ajax
from src.data_utils import get_fname_for_participating_games_based_on_ajax
from src.data_utils import (
    get_fname_for_participating_games_with_unknown_demo_based_on_ajax,
    get_fname_for_event_json_data,
    load_event_apps,
    load_event_demos,
    load_event_apps_with_unknown_demo,
    load_event_json_data,
)
from src.disk_utils import save_txt, save_json
from src.utils import chunks
from src.utils import to_str


def get_host():
    return "https://store.steampowered.com"


def get_flavor_candidates():
    return [
        "DailyActiveUserDemo",
        "Discounted",
        "MostPlayedDemo",
        "PlayedNowDemo",
        "PopularComingSoon",
        "PopularPurchased",
        "PopularPurchasedDiscounted",
        "PopularUpcoming",
        "Price",
        "RecentlyReleased",
        "TopWishlisted",
        "TrendingWishlisted",
    ]


def run_ajax_query_for_apps(flavor="popularpurchased", step_size=None, verbose=True):
    # Reference: https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-Sale-Dynamic-App-Query
    app_endpoint = "/saleaction/ajaxgetsaledynamicappquery"

    app_params = {
        "cc": "FR",
        "clanAccountID": 39049601,
        "clanAnnouncementGID": 3337742851854054341,
        "flavor": flavor,
        "start": 0,  # TODO change value
        "count": 100,  # max value
    }

    if step_size is None:
        step_size = app_params["count"]

    event_appids = []
    possible_has_more = True
    expected_num_appids = None

    while possible_has_more:
        r = requests.get(url=get_host() + app_endpoint, params=app_params)

        if r.ok:
            data = r.json()

            event_appids += data["appids"]
            possible_has_more = data["possible_has_more"]
            if expected_num_appids is None:
                expected_num_appids = data["match_count"]
            if verbose:
                print(len(set(event_appids)))
            app_params["start"] += step_size
        else:
            print(f"Error {r.status_code}")
            break

    if verbose:
        print(f"Expected {expected_num_appids}")
        print(len(event_appids))
        print(len(set(event_appids)))

    event_appids = sorted(set(event_appids))

    return event_appids


def run_ajax_query_for_demos(event_appids, chunk_size=None, verbose=True):
    # Reference: https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-Demo-Events
    demo_endpoint = "/saleaction/ajaxgetdemoevents"

    demo_params = {"appids[]": ""}  # TODO change value

    if chunk_size is None:
        chunk_size = get_optimal_chunk_size()

    demo_ids = []
    app_ids_with_unknown_demo = []
    json_data = {}

    for appid_batch in chunks(event_appids, chunk_size):
        param_array = "?appids[]="
        param_array += "&appids[]=".join(to_str(appid_batch))

        r = requests.get(url=get_host() + demo_endpoint + param_array)

        if r.ok:
            data = r.json()

            for app in data["info"]:
                app_id = app["appid"]
                demo_id = app["demo_appid"]
                if demo_id == 0:
                    app_ids_with_unknown_demo.append(app_id)
                    if app_id not in json_data:
                        json_data[app_id] = demo_id
                else:
                    demo_ids.append(demo_id)
                    json_data[app_id] = demo_id

            if verbose:
                num_demos = len(set(demo_ids))
                num_unknown_apps = len(set(app_ids_with_unknown_demo))
                print(
                    f"demos: #known = {num_demos} ; #unknown = {num_unknown_apps} ; total = {num_demos + num_unknown_apps}"
                )
        else:
            print(f"Error {r.status_code}")
            data = {}
            break

    if verbose:
        print(f"Expected {len(event_appids)}")

        num_demos = len(demo_ids)
        num_unknown_apps = len(app_ids_with_unknown_demo)
        print(
            f"demos: #known = {num_demos} ; #unknown = {num_unknown_apps} ; total = {num_demos + num_unknown_apps}"
        )

        num_demos = len(set(demo_ids))
        num_unknown_apps = len(set(app_ids_with_unknown_demo))
        print(
            f"demos: #known = {num_demos} ; #unknown = {num_unknown_apps} ; total = {num_demos + num_unknown_apps}"
        )

    demo_ids = sorted(set(demo_ids))
    app_ids_with_unknown_demo = sorted(set(app_ids_with_unknown_demo))

    return demo_ids, app_ids_with_unknown_demo, json_data


def create_event_files_for_apps_from_scratch(step_size=None, verbose=True):
    event_appids = set()
    # Caveat: it is important to iterate over flavors, which result in different sorting orders, in order to get
    # exhaustive results. Otherwise, results returned by the API seem redundant, and we end up missing a few,
    # unless we significantly decrease the step-size, thus send a lot more requests and require some luck.
    for flavor in get_flavor_candidates():
        print(f"Flavor: {flavor}")
        new_event_appids = run_ajax_query_for_apps(
            flavor=flavor, step_size=step_size, verbose=verbose
        )
        event_appids = event_appids.union(new_event_appids)

    event_appids = sorted(set(event_appids))

    if verbose:
        print(f"#appids = {len(event_appids)}")

    save_txt(event_appids, fname=get_fname_for_participating_games_based_on_ajax())

    return event_appids


def create_event_files_for_demos_from_scratch(chunk_size=None, verbose=True):
    # NB: a demo seems missing. Don't worry: this is for the appID: 1880360, which corresponds to the DLC called
    # "Monster Hunter Rise: Sunbreak". Actually, there are 2 apps (base game and DLC) which point to the same demo,
    # so the demo is would be a duplicate anyway.

    event_appids = load_event_apps()

    demo_ids, app_ids_with_unknown_demo, json_data = run_ajax_query_for_demos(
        event_appids, chunk_size=chunk_size, verbose=verbose
    )
    save_txt(demo_ids, fname=get_fname_for_participating_demos_based_on_ajax())
    save_txt(
        app_ids_with_unknown_demo,
        fname=get_fname_for_participating_games_with_unknown_demo_based_on_ajax(),
    )
    save_json(json_data, get_fname_for_event_json_data())

    return demo_ids, app_ids_with_unknown_demo, json_data


def update_json_data(json_data, new_json_data):
    for app_id, demo_id in new_json_data.items():
        if demo_id != 0 or app_id not in json_data:
            json_data[app_id] = demo_id
    return json_data


def save_new_event_files(new_demo_ids, new_app_ids_with_unknown_demo, new_json_data):
    demo_ids = load_event_demos() + new_demo_ids
    app_ids_with_unknown_demo = new_app_ids_with_unknown_demo

    json_data = load_event_json_data()
    json_data = update_json_data(json_data, new_json_data)

    demo_ids = sorted(set(demo_ids))
    app_ids_with_unknown_demo = sorted(set(app_ids_with_unknown_demo))

    if len(new_demo_ids) > 0:
        print(f"[{datetime.datetime.now()}] Updating AJAX-based files. 🎂")
        save_txt(demo_ids, fname=get_fname_for_participating_demos_based_on_ajax())
        save_txt(
            app_ids_with_unknown_demo,
            fname=get_fname_for_participating_games_with_unknown_demo_based_on_ajax(),
        )
        save_json(json_data, get_fname_for_event_json_data())

    return


def update_event_files(chunk_size=None, verbose=False):
    app_ids_with_unknown_demo = load_event_apps_with_unknown_demo()

    (
        new_demo_ids,
        new_app_ids_with_unknown_demo,
        new_json_data,
    ) = run_ajax_query_for_demos(
        app_ids_with_unknown_demo, chunk_size=chunk_size, verbose=verbose
    )

    save_new_event_files(new_demo_ids, new_app_ids_with_unknown_demo, new_json_data)

    return new_demo_ids


def get_optimal_step_size():
    max_step_size = 100
    step_size = max_step_size
    return step_size


def get_optimal_chunk_size():
    max_chunk_size = 250
    chunk_size = max_chunk_size
    return chunk_size


def initialize_event_files(verbose=False):
    event_appids = create_event_files_for_apps_from_scratch(
        step_size=get_optimal_step_size(), verbose=verbose
    )
    (
        demo_ids,
        app_ids_with_unknown_demo,
        json_data,
    ) = create_event_files_for_demos_from_scratch(
        chunk_size=get_optimal_chunk_size(), verbose=verbose
    )

    return


def perform_incremental_update_of_event_files(verbose=False):
    new_demo_ids = update_event_files(
        chunk_size=get_optimal_chunk_size(), verbose=verbose
    )
    return new_demo_ids


def main():
    # initialize_event_files(verbose=True)
    new_demo_ids = perform_incremental_update_of_event_files(verbose=True)

    return


if __name__ == "__main__":
    main()
