from src.disk_utils import load_file
from src.utils import to_int


def get_data_folder():
    return "data/"


def get_fname_for_event_json_data():
    return get_data_folder() + "event_data.json"


def get_fname_for_participating_demos_based_on_ajax():
    # Reference: run_ajax_queries.py
    return get_data_folder() + "event_demo_ids.txt"


def get_fname_for_participating_games_based_on_ajax():
    # Reference: run_ajax_queries.py
    return get_data_folder() + "event_app_ids.txt"


def get_fname_for_participating_games_with_unknown_demo_based_on_ajax():
    # Reference: run_ajax_queries.py
    return get_data_folder() + "event_app_ids_with_unknown_demo.txt"


def get_fname_for_all_known_apps():
    # Reference: list_all_known_ids.py
    return get_data_folder() + "known_ids.txt"


def get_fname_for_unfiltered_demos():
    # Reference: list_unowned_demos.py
    return get_data_folder() + "demo_ids_unfiltered.txt"


def get_fname_for_participating_demos():
    # Reference: list_relevant_unowned_apps.py
    return get_data_folder() + "demo_ids.txt"


def get_fname_for_participating_games():
    # Reference: https://steamdb.info/sales/?event=3337742851854054341
    return get_data_folder() + "game_names.txt"


def get_fname_for_app_store():
    # Reference: https://api.steampowered.com/ISteamApps/GetAppList/v2/
    return get_data_folder() + "ISteamApps.json"


def get_fname_for_owned_ids():
    # Reference:
    # - https://github.com/ValvePython/steamctl (required in order to have ids of owned demos)
    # - https://store.steampowered.com/dynamicstore/userdata/ (avoid, because this does not include demos)
    return get_data_folder() + "owned_ids.txt"


def get_fname_for_demos_already_counted():
    return get_data_folder() + 'demo_ids_already_counted.txt'


def extract_app_list(app_store_data, verbose=True):
    try:
        app_list = app_store_data["applist"]["apps"]
    except KeyError:
        app_list = []

    if verbose:
        num_apps = len(app_list)
        print(f"#apps = {num_apps}")

    return app_list


def load_event_json_data():
    json_data = load_file(fname=get_fname_for_event_json_data())
    return json_data


def load_event_apps():
    appids = load_file(fname=get_fname_for_participating_games_based_on_ajax())
    return to_int(appids)


def load_event_demos():
    appids = load_file(fname=get_fname_for_participating_demos_based_on_ajax())
    return to_int(appids)


def load_event_apps_with_unknown_demo():
    appids = load_file(fname=get_fname_for_participating_games_with_unknown_demo_based_on_ajax())
    return to_int(appids)


def load_known_apps():
    appids = load_file(fname=get_fname_for_all_known_apps())
    return to_int(appids)


def load_unfiltered_demos():
    appids = load_file(fname=get_fname_for_unfiltered_demos())
    return to_int(appids)


def load_demos():
    appids = load_file(fname=get_fname_for_participating_demos())
    return to_int(appids)


def load_games():
    app_names = load_file(fname=get_fname_for_participating_games())
    return app_names


def load_store_app_list(verbose=True):
    app_data = load_file(fname=get_fname_for_app_store())
    return extract_app_list(app_data, verbose=verbose)


def load_owned_apps():
    appids = load_file(fname=get_fname_for_owned_ids())
    return to_int(appids)


def load_demos_already_counted():
    appids = load_file(fname=get_fname_for_demos_already_counted())
    return to_int(appids)
