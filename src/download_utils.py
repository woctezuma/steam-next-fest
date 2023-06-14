import requests


def get_store_api_url():
    return "https://api.steampowered.com/ISteamApps/GetAppList/v2/"


def download_store_data():
    r = requests.get(url=get_store_api_url())

    if r.ok:
        data = r.json()
    else:
        print(f"Error: {r.status_code}")
        data = {}

    return data
