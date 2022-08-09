import json


def load_device_info(my_path="./device_info/DEVICES-KEY.json"):
    try:
        with open(my_path, "r") as f:
            row_data = json.load(f)
    except FileNotFoundError:
        return None
    return row_data


if __name__ == '__main__':
    load_device_info()
    pass
