from src.utils import to_str
from ASF import IPC


def get_addlicense_command(appids):
    return "addlicense a/" + ",a/".join(to_str(appids))


def get_play_command(appids):
    return "play " + ",".join(to_str(appids))


def get_resume_command():
    return "resume"


async def send_command(asf, cmd, verbose=True):
    # Reference: https://github.com/deluxghost/ASF_IPC
    resp = await asf.Api.Command.post(body={"Command": cmd})

    if verbose:
        if resp.success:
            print(resp.result)
        else:
            print(f"Error: {resp.message}")

    return resp


async def addlicense(asf, appids):
    return await send_command(asf, get_addlicense_command(appids))


async def play(asf, appids):
    return await send_command(asf, get_play_command(appids))


async def resume(asf):
    return await send_command(asf, get_resume_command())


async def add_and_play(appids):
    async with IPC() as asf:
        await addlicense(asf, appids)
        await play(asf, appids)
        await resume(asf)

    return
