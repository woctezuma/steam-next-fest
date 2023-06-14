from src.data_utils import get_fname_for_app_store, extract_app_list
from src.disk_utils import save_json
from src.download_utils import download_store_data


def is_store_data_valid(app_store_data, verbose=False):
    app_list = extract_app_list(app_store_data, verbose=verbose)
    return bool(len(app_list) > 0)


def update_cache_of_store_data(verbose=False):
    app_store_data = download_store_data()

    if is_store_data_valid(app_store_data, verbose=verbose):
        save_json(app_store_data, fname=get_fname_for_app_store())

    return app_store_data


def main():
    app_store_data = update_cache_of_store_data(verbose=True)

    return


if __name__ == "__main__":
    main()
