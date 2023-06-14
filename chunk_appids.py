from src.data_utils import load_event_demos
from src.utils import chunks


def display_asf_lines_to_copy_paste(command_name, app_ids=None, verbose=False):
    command_name_trimmed_from_bot_names = command_name.split()[0]
    assert command_name_trimmed_from_bot_names in ["owns", "addlicense", "play"]

    if app_ids is None:
        app_ids = load_event_demos()
        app_ids = sorted(list(app_ids), reverse=True)

    if verbose:
        print(f"#apps = {len(app_ids)}")

    if command_name.startswith("play"):
        batch_size = 32
    else:
        batch_size = 50

    if command_name.startswith("addlicense"):
        prefixe = "a/"
        separator = ",a/"
    else:
        prefixe = ""
        separator = ","

    for s in chunks(app_ids, batch_size):
        print(f"!{command_name} {prefixe}" + separator.join(str(i) for i in s))

    return


if __name__ == "__main__":
    display_asf_lines_to_copy_paste(command_name="owns")
    display_asf_lines_to_copy_paste(command_name="addlicense")
    display_asf_lines_to_copy_paste(command_name="play")
