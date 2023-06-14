from src.data_utils import get_fname_for_unfiltered_demos
from src.data_utils import load_store_app_list, load_owned_apps
from src.disk_utils import save_txt


def keep_track_of_unowned_demos():
    # We keep **unowned** **DEMOS**, irrespective of the games participating in the event.
    app_list = load_store_app_list(verbose=False)
    owned_appids = load_owned_apps()

    demo_ids = [int(app["appid"]) for app in app_list if app["name"].strip().endswith(' Demo')]
    unowned_demo_ids = set(demo_ids).difference(owned_appids)

    unowned_demos = sorted(unowned_demo_ids)
    save_txt(unowned_demos, get_fname_for_unfiltered_demos())

    return unowned_demos


def main():
    ## Previously, slow unoptimized code:
    # keep_all_unowned_apps = False
    # app_dict = load_store_unowned_demo_dict(keep_all_unowned_apps)
    # unowned_demos = sorted(app_dict.values())
    # Then save!

    ## Now, much faster code:
    unowned_demos = keep_track_of_unowned_demos()

    return


if __name__ == "__main__":
    main()
