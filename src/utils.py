def to_str(appids):
    return [str(id) for id in appids]


def to_int(appids):
    return [int(id) for id in appids]


# Reference: https://stackoverflow.com/a/312464/376454
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
