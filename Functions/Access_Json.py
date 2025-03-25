import json
import os

INFO_FILE = './info.json'

def load_data():
    if os.path.exists(INFO_FILE):
        with open(INFO_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_data(key, value):
    data = load_data()
    data[key] = value
    with open(INFO_FILE, 'w') as file:
        json.dump(data, file, indent=4)
