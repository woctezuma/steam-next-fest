from chunk_appids import display_asf_lines_to_copy_paste
from find_missing_demos_in_ISteamApps import build_app_dict
from src.data_utils import load_event_json_data, load_event_demos, get_fname_for_demos_already_counted
from src.demo_utils import check_if_owned_demos
from src.disk_utils import load_file, save_txt


def convert_names_to_ids(target_names, app_dict=None, event_data=None):
    if app_dict is None:
        app_dict = build_app_dict(verbose=False)

    if event_data is None:
        event_data = load_event_json_data()

    demo_ids = []
    app_names_with_error_for_game = []
    app_ids_with_error_for_demo = []

    for name in target_names:
        name = name.strip()

        demo_suffixe = " Demo"
        if name.endswith(demo_suffixe):
            name = name[: -len(demo_suffixe)]

        try:
            id = app_dict[name]
        except KeyError:
            id = None

        demo_name = name + " Demo"

        try:
            demo_id = app_dict[demo_name]
        except KeyError:
            try:
                demo_id = event_data[str(id)]
            except KeyError:
                demo_id = None

        if demo_id is None or demo_id == 0:
            if id is None:
                app_names_with_error_for_game.append(name)
            else:
                app_ids_with_error_for_demo.append(id)
        else:
            demo_ids.append(demo_id)

    demo_ids = sorted(set(demo_ids))
    app_names_with_error_for_game = sorted(set(app_names_with_error_for_game))
    app_ids_with_error_for_demo = sorted(set(app_ids_with_error_for_demo))

    return demo_ids, app_names_with_error_for_game, app_ids_with_error_for_demo


def fix_wrong_game_name(game_names):
    # The entry "Unknown" is actually "Celeritas" (a/1974440), which has a demo (a/2055710) in Steam Next Fest.
    # The reason why the entry does not reveal the name of the base game is that the store page was taken offline.
    replacements = {'Unknown': 'Celeritas'}

    for i, s in enumerate(game_names):
        for wrong_name, fixed_name in replacements.items():
            if s.strip() == wrong_name:
                game_names[i] = fixed_name
                break
    return game_names


def get_additional_entries():
    # Data manually retrieved from SteamDB using the title in Asian characters rather than Latin characters.
    additional_entries = [  # 3 values: app_name ; app_id ; demo_id
        ["Demon Speakeasy", 1854250, 1978530], ["Depersonalization", 1477070, 1490520],
        ["DragonSpirits2", 1965190, 2027320], ["Glimmer in Mirror", 1035760, 1431000],
        ["I AM BUTTER", 1859180, 1982780], ["Level 1 Me & The Final Dungeon", 1307740, 2015590],
        ["Love with You", 1814380, 1928720], ["Mercury Abbey", 1689080, 1947770],
        ["Monster Stalker: Prologue", 1936710, 2024200], ["Ninja Soul", 1848710, 1856960],
        ["Online Sparkler", 1965390, 2024850], ["Panzer Girls", 1844150, 1986090],
        ["Phantom Thief Mew's Secret Prima", 1728390, 2014250], ["QUIT TODAY", 1858450, 1913390],
        ["Raid on Taihoku", 1901950, 1908910], ["Starchild Velta and loadtosky", 1909740, 1920220],
        ["The Heroes Around Me", 1768470, 1852270], ["The Misanthropic Girl", 1714770, 2012870],
        ["The witch of the Ihanashi", 1950570, 1957470], ["Whisper Books", 1970300, 2000410],
        ["Zhijiang Town", 1914940, 1919660], ["xiuzhen idle", 1649730, 1935010], ["Kebab Simulator", 1001270, 2009050],
        ["KiNoKoe : Tree's Voice", 1846710, 1964710], ]
    return additional_entries


def add_entries_to_app_dict(app_dict):
    additional_entries = get_additional_entries()

    for app in additional_entries:
        name = app[0].strip()
        id = int(app[1])
        demo_id = int(app[2])
        demo_name = f"{name} Demo"

        app_dict[id] = name
        app_dict[name] = id

        app_dict[demo_id] = demo_name
        app_dict[demo_name] = demo_id

    return app_dict


def add_entries_to_event_data(event_data):
    additional_entries = get_additional_entries()

    for app in additional_entries:
        id = app[1]
        demo_id = app[2]

        event_data[str(id)] = int(demo_id)

    return event_data


def compute_and_save_already_counted_demo_ids(save_to_disk=True, verbose=True):
    # Reference: https://help.steampowered.com/accountdata/NextFestDemoPlays
    game_names = load_file("data/Next_Fest_1053_demos_17_June.txt")
    game_names = fix_wrong_game_name(game_names)

    app_dict = build_app_dict(verbose=False)
    app_dict = add_entries_to_app_dict(app_dict)

    event_data = load_event_json_data()
    event_data = add_entries_to_event_data(event_data)

    ## Look for demo IDs one way

    (demo_ids, app_names_with_keyerror_for_game, app_ids_with_keyerror_for_demo,) = convert_names_to_ids(game_names,
                                                                                                         app_dict=app_dict,
                                                                                                         event_data=event_data)

    t = len(game_names)
    u = len(demo_ids)
    v = len(app_names_with_keyerror_for_game)
    w = len(app_ids_with_keyerror_for_demo)

    print(f"#demos (input): {t}\n#demos (output) -> 👍: {u} ; #game 👎: {v} ; #demo 👎: {w} ; total: {u + v + w}")

    if verbose:
        print('---')
        print('\n'.join(app_names_with_keyerror_for_game))
        print('---')
        print('\n'.join(str(id) for id in app_ids_with_keyerror_for_demo))
        print('---')

    demo_ids = sorted(demo_ids)
    if save_to_disk:
        save_txt(demo_ids, fname=get_fname_for_demos_already_counted())

    return demo_ids


def main():
    save_to_disk = False
    verbose = False

    ## Find demo IDs which have already been counted by the Steam Next Fest badge
    demo_ids = compute_and_save_already_counted_demo_ids(save_to_disk=save_to_disk, verbose=verbose)

    ## Find demo IDs which would still be expected
    expected_demo_ids = load_event_demos()
    still_expected_demo_ids = set(expected_demo_ids).difference(demo_ids)

    bot_name = ''
    check_if_owned_demos(list(still_expected_demo_ids), bot_name=bot_name)

    base_command_name = 'addlicense'
    display_asf_lines_to_copy_paste(f'{base_command_name} {bot_name}', app_ids=list(still_expected_demo_ids))

    ## Call ASF
    aggregated_ids = set(demo_ids) | set(still_expected_demo_ids)

    bot_name = 'wok,woknoob,woksmurf'
    # play_demos(list(aggregated_ids), bot_name=bot_name)

    return


if __name__ == "__main__":
    main()
