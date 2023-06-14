from src.data_utils import get_fname_for_participating_demos
from src.data_utils import load_event_apps, load_unfiltered_demos, load_event_apps_with_unknown_demo
from src.data_utils import load_store_app_list, load_owned_apps
from src.disk_utils import save_txt
from src.filter_utils import get_demo_suffixe


def find_candidate_matches(game_names, app_dict, verbose=True):
    # Slow unoptimized code?

    demo_ids_to_monitor = []

    for game_name in game_names:
        game_name = game_name.strip()
        demo_name = game_name + get_demo_suffixe()

        new_ids = []

        for app_name, app_id in app_dict.items():
            if game_name == app_name:
                continue

            if demo_name == app_name:
                if verbose:
                    print(f"[{app_id}] {demo_name} 👌")
                new_ids = [app_id]
                break

            if game_name in app_name:
                if verbose:
                    print(f"[{app_id}] {game_name} -> close to {app_name}")
                new_ids.append(app_id)

        demo_ids_to_monitor += new_ids

    if verbose:
        num_ids = len(demo_ids_to_monitor)
        print(f"#ids = {num_ids}")

    return demo_ids_to_monitor


def get_short_list_of_mysterious_game_names(d):
    game_names = []
    for id in load_event_apps_with_unknown_demo():
        try:
            name = d[id]
        except KeyError:
            name = None
        if name is not None:
            game_names.append(name)

    return game_names


def keep_track_of_other_relevant_unowned_apps():
    # We keep **unowned** APPS which:
    # - **match** games participating in the event, hence "relevant",
    # - might have been missed by other scripts, hence "other" than i) demos or ii) the base games themselves.

    owned_appids = load_owned_apps()
    unowned_demo_ids = load_unfiltered_demos()  # TODO run list_unowned_demos.py first to populate the file!

    excluded_ids = set(owned_appids).union(unowned_demo_ids)

    app_list = load_store_app_list(verbose=False)
    d = {app["appid"]: app["name"].strip() for app in app_list if app["appid"] not in excluded_ids}

    ## Slow:
    # game_names = [name.strip() for name in load_games()]
    ## Faster by keeping the list of game names short: focus on event apps for which the demo is unknown!
    game_names = get_short_list_of_mysterious_game_names(d)

    relevant_ids = set(int(id) for id, name in d.items() if any(s in name for s in game_names))

    # We remove event appIDs, because we don't want matches with the exact games.
    # However, we do it at the very end, because we rely on the dictionary d to obtain the **short** list game_names.
    # If you add event appIDs to excluded IDs near the beginning, then you would have an empty list game_names. Careful!
    event_appids = load_event_apps()
    relevant_ids = relevant_ids.difference(event_appids)

    relevant_ids = sorted(relevant_ids)
    save_txt(relevant_ids, get_fname_for_participating_demos())

    return relevant_ids


def main():
    ## Previously, slow unoptimized code:
    # keep_all_unowned_apps = True
    # game_names = [name.strip() for name in load_games()]
    # app_dict = load_store_unowned_demo_dict(keep_all_unowned_apps)
    # relevant_ids = find_candidate_matches(game_names, app_dict, verbose=True)
    # Then save!

    ## Now, much faster code:
    relevant_ids = keep_track_of_other_relevant_unowned_apps()

    return


if __name__ == "__main__":
    main()
