import json


def load_json(fname):
    with open(fname, "r", encoding="utf8") as f:
        data = json.load(f)
    return data


def save_json(data, fname):
    with open(fname, "w", encoding="utf8") as f:
        json.dump(data, f)
    return


def load_txt(fname):
    with open(fname, "r", encoding="utf8") as f:
        data = [line.strip() for line in f.readlines()]
    return data


def save_txt(data, fname):
    with open(fname, "w", encoding="utf8") as f:
        for line in data:
            f.write(f"{str(line)}\n")
    return


def load_file(fname):
    if fname.endswith(".json"):
        data = load_json(fname)
    elif fname.endswith(".txt"):
        data = load_txt(fname)
    else:
        data = None
    return data
