import asyncio

from src.asf_utils import add_and_play


def play_demos(appids):
    loop = asyncio.get_event_loop()
    output = loop.run_until_complete(add_and_play(appids))
    loop.close()

    return output
