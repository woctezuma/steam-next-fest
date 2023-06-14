import json

from steam.client import SteamClient

client = SteamClient()
client.anonymous_login()

apps = [2059470]
out = client.get_product_info(apps=apps)
print(out)

with open('temp.json', 'w') as f:
    json.dump(out, f, indent=4, sort_keys=True)

client.logout()
