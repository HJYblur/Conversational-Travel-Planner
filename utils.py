import os
import json
from event import Event
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


def append_to_json(agent_question, user_text, id):
    '''
    Append a new entry to the specified JSON file
    '''
    file_path = os.path.join(config['settings']['user_path'], "ice_breaker.json")

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []

    new_entry = {
        "id": str(id),
        "agent_question": agent_question,
        "user_text": user_text
    }

    data.append(new_entry)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_json(file_path):
    '''
    Load a JSON file from the given file path and return a list
    '''
    with open(os.path.join(config['settings']['user_path'], file_path), 'r') as file:
        data = json.load(file)
    return list(data.values())


def load_event_json(file_path = "event.json"):
    '''
    Load a JSON file which is a list
    '''
    with open(os.path.join(config['settings']['user_path'], file_path), 'r') as file:
        events_data = json.load(file)

    # Convert JSON data to Event instances
    return [Event.from_dict(event).extract() for event in events_data]


def save_json(data, file_path):
    '''
    Save a JSON file to the given file path
    '''
    with open(os.path.join(config['settings']['user_path'], file_path), 'w') as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
     memory_text = load_json('preference.json')
     print(memory_text)