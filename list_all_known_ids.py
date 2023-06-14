from src.data_utils import get_fname_for_all_known_apps
from src.data_utils import load_store_app_list
from src.disk_utils import save_txt


def compute_known_ids(save_to_disk=True):
    app_list = load_store_app_list(verbose=False)
    known_ids = [int(app["appid"]) for app in app_list]

    known_ids = sorted(known_ids)

    if save_to_disk:
        save_txt(known_ids, get_fname_for_all_known_apps())

    return known_ids


def main():
    # We keep **ALL** **APPS**, no matter of the ownership, and irrespective of the games participating in the event.
    known_ids = compute_known_ids(save_to_disk=True)

    return


if __name__ == "__main__":
    main()
