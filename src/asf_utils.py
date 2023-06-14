import datetime

from ASF import IPC

from src.utils import to_str


def format_appid_list_as_str(appids, prefixe=""):
    separator = f',{prefixe}'
    appid_list_as_str = prefixe + separator.join(to_str(appids))
    return appid_list_as_str


def get_addlicense_command(appids, bot_name=""):
    # Reference: https://github.com/JustArchiNET/ArchiSteamFarm/wiki/Commands#addlicense-licenses
    command_name = 'addlicense'
    appid_list_as_str = format_appid_list_as_str(appids, prefixe='a/')
    return f"{command_name} {bot_name} {appid_list_as_str}"


def get_play_command(appids, bot_name=""):
    # Reference: https://github.com/JustArchiNET/ArchiSteamFarm/wiki/Commands
    command_name = 'play'
    appid_list_as_str = format_appid_list_as_str(appids)
    return f"{command_name} {bot_name} {appid_list_as_str}"


def get_owns_command(appids, bot_name=""):
    # Reference: https://github.com/JustArchiNET/ArchiSteamFarm/wiki/Commands#owns-games
    command_name = 'owns'
    appid_list_as_str = format_appid_list_as_str(appids)
    return f"{command_name} {bot_name} {appid_list_as_str}"


def get_resume_command(bot_name=""):
    # Reference: https://github.com/JustArchiNET/ArchiSteamFarm/wiki/Commands
    command_name = 'reset'  # TODO resume or reset? Which one would be the fastest? Go for PAUSE?
    return f"{command_name} {bot_name}"


async def send_command(asf, cmd, verbose=True):
    if verbose:
        print(f"[{datetime.datetime.now()}] send: {cmd}")

    # Reference: https://github.com/deluxghost/ASF_IPC
    resp = await asf.Api.Command.post(body={"Command": cmd})

    if verbose:
        if resp.success:
            print(f"[{datetime.datetime.now()}] done: {cmd}")
            print(resp.result.strip())
        else:
            print(f"Error: {resp.message}")

    return resp


async def addlicense(asf, appids, bot_name="", verbose=True):
    return await send_command(asf, get_addlicense_command(appids, bot_name), verbose=verbose)


async def play(asf, appids, bot_name="", verbose=True):
    return await send_command(asf, get_play_command(appids, bot_name), verbose=verbose)


async def resume(asf, bot_name="", verbose=True):
    return await send_command(asf, get_resume_command(bot_name), verbose=verbose)


async def owns(asf, appids, bot_name="", verbose=True):
    return await send_command(asf, get_owns_command(appids, bot_name), verbose=verbose)


def get_asf_output_as_str(asf_response):
    if asf_response is None:
        asf_output = ''
    else:
        asf_output = asf_response.result
    return asf_output


def has_activated_a_new_package(asf_response):
    asf_output = get_asf_output_as_str(asf_response)
    return bool('sub/' in asf_output)


def is_playable(asf_response):
    # After calling 'addlicense a/appID', ASF returns a message indicating that the app a/appID:
    # - was already playable:
    #   > <Wok> ID : app/2057960 | Statut : OK | Items : app/2057960
    # - is owned and playable as the result of the package activation:
    #   > <Wok> ID : app/2058710 | Statut : OK | Items : app/2058710, sub/735487
    # - is not playable, usually because it is still NOT owned.
    #   However, *owned* apps can match here after they were completely removed from Steam and made unplayable by devs.
    #   > <Wok> ID : app/1883860 | Statut : OK
    # So the mention "Items" is the marker of app **playability** after the 'addlicense' command.
    asf_output = get_asf_output_as_str(asf_response)
    return bool('Items' in asf_output)


async def add_and_play(appids, bot_name="", resume_afterwards=True):
    async with IPC() as asf:
        asf_response = await addlicense(asf, appids, bot_name)
        if is_playable(asf_response):
            await play(asf, appids, bot_name)
            if resume_afterwards:
                await resume(asf, bot_name)

    return


async def only_play(appids, bot_name="", resume_afterwards=True):
    async with IPC() as asf:
        await play(asf, appids, bot_name=bot_name)
        if resume_afterwards:
            await resume(asf, bot_name)

    return


async def check_if_owned(appids, bot_name=""):
    async with IPC() as asf:
        await owns(asf, appids, bot_name=bot_name)

    return


async def process_appids(appids_to_process, owned_appids, resume_afterwards=False, keyword="", verbose=True):
    if verbose:
        current_time = datetime.datetime.now()
        print(f"[{current_time}] Contacting ASF 👀 {appids_to_process}")

    owned_appids_to_process = appids_to_process & owned_appids
    unowned_appids_to_process = appids_to_process - owned_appids_to_process

    if len(unowned_appids_to_process) > 0:
        await add_and_play(list(unowned_appids_to_process), resume_afterwards=resume_afterwards)
        if verbose:
            current_time = datetime.datetime.now()
            print(f"[{current_time}] ASF/unowned/{keyword} 👌 {unowned_appids_to_process}")

    if len(owned_appids_to_process) > 0:
        await only_play(list(owned_appids_to_process), resume_afterwards=resume_afterwards)
        if verbose:
            current_time = datetime.datetime.now()
            print(f"[{current_time}] ASF/owned/{keyword} 👌 {owned_appids_to_process}")

    return
