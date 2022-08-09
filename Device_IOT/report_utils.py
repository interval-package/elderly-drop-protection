import json


def load_device_info(my_path="./device_info/DEVICES-KEY.json"):
    with open(my_path, "r") as f:
        row_data = json.load(f)
    return row_data


if __name__ == '__main__':
    load_device_info()
    pass
