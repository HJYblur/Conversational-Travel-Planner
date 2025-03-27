import os
import json
from event import Event
from ice_breaker import Ice_breaker
from configure_loader import load_config
config = load_config()


def init_json(file_name = "ice_breaker.json"):
    '''
    Initialize a JSON file, this function will automatilly clean it
    '''
    file_path = os.path.join(config['settings']['user_path'], file_name)
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump([], file, indent=4, ensure_ascii=False)
        return True


def append_to_json(summarized_tuple, id, irony=False, file_name = "ice_breaker.json"):
    '''
    Append a new entry to the specified JSON file
    '''
    file_path = os.path.join(config['settings']['user_path'],file_name)

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []

    if file_name == "ice_breaker.json":
        new_entry = {
            "id": str(id),
            "summarized_tuple": summarized_tuple,
        }

    else:
        new_entry = {
            "id": str(id),
            "summarized_tuple": summarized_tuple,
            "irony": irony,
        }

    data.append(new_entry)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)



def load_json(memory_type):
    '''
    Load a JSON file which is a list
    '''
    file_path = "event.json" if memory_type == "event" else  "ice_breaker.json"
    with open(os.path.join(config['settings']['user_path'], file_path), 'r') as file:
        data = json.load(file)

    # Convert JSON data to Event/Ice_breaker instances
    if memory_type == 'event':
        return [Event.from_dict(event).extract() for event in data]
    else:
        return [Ice_breaker.from_dict(pref).extract() for pref in data]


def get_json_size(memory_type):
    file_path = "event.json" if memory_type == "event" else  "ice_breaker.json"
    with open(os.path.join(config['settings']['user_path'], file_path), 'r') as file:
        data = json.load(file)
        return len(data)