# Activate and play demos on bot accounts

from chunk_appids import display_asf_lines_to_copy_paste


def get_appid_batches():
    batches = [
        [],
    ]

    print(f'#batches = {len(batches)}')

    return batches


def main(batch_no):
    appid_batches = get_appid_batches()
    assert (0 <= batch_no < len(appid_batches))

    bot_names = ','.join(['woknoob', 'woksmurf'])

    # check_if_owned_demos([id for l in appid_batches for id in l], bot_name=bot_names)

    for command_name in ['addlicense', 'play']:
        display_asf_lines_to_copy_paste(f'{command_name} {bot_names}', app_ids=appid_batches[batch_no])

    return


if __name__ == "__main__":
    main(batch_no=0)
