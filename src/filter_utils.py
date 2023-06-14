from src.data_utils import load_store_app_list, load_owned_apps


def get_demo_suffixe():
    return " Demo"


def is_demo(app_name):
    return app_name.endswith(get_demo_suffixe())


def extract_unowned_demos(app_list, owned_appids, keep_all_unowned_apps=False):
    app_dict = {}

    for app in app_list:
        id = int(app["appid"])
        name = app["name"].strip()

        if id in owned_appids:
            continue

        if keep_all_unowned_apps or is_demo(name):
            app_dict[name] = id

    return app_dict


def load_store_unowned_demo_dict(keep_all_unowned_apps=False):
    app_list = load_store_app_list(verbose=False)
    owned_appids = load_owned_apps()

    app_dict = extract_unowned_demos(app_list, owned_appids, keep_all_unowned_apps)
    return app_dict
