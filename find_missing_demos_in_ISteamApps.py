from run_ajax_queries import save_new_event_files
from src.data_utils import load_event_apps_with_unknown_demo
from src.data_utils import load_store_app_list


def build_app_dict(app_list=None, verbose=True):
    if app_list is None:
        app_list = load_store_app_list(verbose=verbose)

    app_dict = {}
    for app in app_list:
        id = int(app["appid"])
        name = app["name"].strip()
        if name != "":
            app_dict[id] = name
            app_dict[name] = id

    return app_dict


def find_missing_demos(app_dict, app_ids_with_unknown_demo):
    new_demo_ids = []
    new_app_ids_with_known_demo = []
    new_json_data = {}

    for id in app_ids_with_unknown_demo:
        try:
            name = app_dict[id]
        except KeyError:
            continue

        name = name.strip()
        if name.endswith(" Demo"):
            demo_name = name
        else:
            demo_name = f"{name} Demo"

        try:
            demo_id = app_dict[demo_name]
        except KeyError:
            continue

        if demo_id != 0:
            new_demo_ids.append(demo_id)
            new_app_ids_with_known_demo.append(id)
            new_json_data[id] = demo_id

    new_app_ids_with_unknown_demo = set(app_ids_with_unknown_demo).difference(
        new_app_ids_with_known_demo
    )
    save_new_event_files(new_demo_ids, new_app_ids_with_unknown_demo, new_json_data)

    return new_demo_ids


def fill_in_event_files_using_ISteamApps(verbose=False):
    app_dict = build_app_dict(verbose=verbose)
    app_ids_with_unknown_demo = load_event_apps_with_unknown_demo()

    new_demo_ids = find_missing_demos(app_dict, app_ids_with_unknown_demo)

    return new_demo_ids


def main():
    new_demo_ids = fill_in_event_files_using_ISteamApps()

    return


if __name__ == "__main__":
    main()
