import asyncio

from chunk_appids import chunks
from src.asf_utils import add_and_play, check_if_owned, only_play


def add_and_play_demos(appids, batch_size=32, bot_name="", resume_afterwards=True):
    for appid_batch in chunks(appids, batch_size):
        asyncio.run(add_and_play(appid_batch, bot_name, resume_afterwards=resume_afterwards))

    return


def check_if_owned_demos(appids, batch_size=50, bot_name=""):
    for appid_batch in chunks(appids, batch_size):
        asyncio.run(check_if_owned(appid_batch, bot_name))

    return


def play_demos(appids, batch_size=32, bot_name="", resume_afterwards=True):
    for appid_batch in chunks(appids, batch_size):
        asyncio.run(only_play(appid_batch, bot_name, resume_afterwards=resume_afterwards))

    return
