# Steam Next Fest

[![Updates][dependency-image]][pyup]
[![Python 3][python3-image]][pyup]
[![Code Quality][codacy-image]][codacy]

This repository contains Python code to play demos for the [Steam Next Fest][steam-next-fest] in June 2022.

![Badge ranking at SteamDB][wiki-cover]

## Requirements

-   Install the latest version of [Python 3.X][python] (at least version 3.10).
-   Install the required packages:

```bash
pip install -r requirements.txt
```

- Install the following softwares:
  - [ArchiSteamFarm][github-ASF] (ASF)
  - [SteamWebPipes][github-SWP] (SWP)

For ASF, make sure that [IPC][wiki-ASF-IPC] is toggled ON.
This is the default value.

For SWP, compile the software and edit the url value:
- from `0.0.0.0:8181` to `localhost:8181`,
- in `SteamWebPipes/SteamWebPipes/bin/Release/settings.json`.

## Usage

- First, run SWP.

- To listen to Steam's events via WebSocket, run:

```bash
python run_SteamWebPipes.py
```

- Then, run ASF.

- To send commands to ASF via IPC, run:

```bash
python run_ASF_IPC.py
```

## References

- The [official webpage][steam-next-fest] for the Steam Next Fest
- Your [Steam badge][your-steam-badge]
- SteamDB's [badge ranking][steamdb-badge-ranking]
- SteamDB's [list of games][steamdb-event-games] participating in the event
- SteamDB's [change history][steamdb-demo-history] for demos
- Steam's [web API][steam-api-calls] to retrieve list of apps on the Steam store
- An [unofficial docuementation][steam-api-doc] of Steam's web API
- Useful softwares:
  - [`JustArchiNET/ArchiSteamFarm`][github-ASF]
  - [`deluxghost/ASF_IPC`][asf-ipc-wrapper]: a wrapper for ASF IPC 
  - [`xPaw/SteamWebPipes`][github-SWP]
  - [`websockets`][pypi-websockets] @ PyPI: a library for building Websocket servers and clients
  - [`ValvePython/steam`][steam-python-package]: a Python module for interacting with Steam
  - [`ValvePython/steamctl`][steamctl-python]: a command-line utility for Steam

<!-- Definitions -->

[steam-next-fest]: <https://store.steampowered.com/sale/nextfest>
[python]: <https://www.python.org/downloads/>
[github-ASF]: <https://github.com/JustArchiNET/ArchiSteamFarm>
[github-SWP]: <https://github.com/xPaw/SteamWebPipes>
[wiki-ASF-IPC]: <https://github.com/JustArchiNET/ArchiSteamFarm/wiki/IPC>
[your-steam-badge]: <https://steamcommunity.com/my/badges/60>
[steamdb-badge-ranking]: <https://steamdb.info/badge/60/>
[steamdb-event-games]: <https://steamdb.info/sales/?event=3337742851854054341>
[steamdb-demo-history]: <https://steamdb.info/history/?filterkey=109>
[steam-api-calls]: <https://github.com/woctezuma/steam-store-snapshots>
[steam-api-doc]: <https://steamapi.xpaw.me/>
[asf-ipc-wrapper]: <https://github.com/deluxghost/ASF_IPC>
[pypi-websockets]: <https://pypi.org/project/websockets/>
[steam-python-package]: <https://github.com/ValvePython/steam>
[steamctl-python]: <https://github.com/ValvePython/steamctl>

[wiki-cover]: <https://github.com/woctezuma/steam-next-fest/wiki/img/level_1050_with_header.png>
[pyup]: <https://pyup.io/repos/github/woctezuma/steam-next-fest/>
[dependency-image]: <https://pyup.io/repos/github/woctezuma/steam-next-fest/shield.svg>
[python3-image]: <https://pyup.io/repos/github/woctezuma/steam-next-fest/python-3-shield.svg>
[codacy]: <https://app.codacy.com/gh/woctezuma/steam-next-fest/>
[codacy-image]: <https://api.codacy.com/project/badge/Grade/7a64d60f823a4c8bb38217055abf3cb1>
