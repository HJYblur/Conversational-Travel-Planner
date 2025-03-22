import yaml
import os
import json
import tkinter as tk
import sounddevice as sd
from gui import AudioPlayerApp
from event import Event
from configure_loader import load_config
import threading
config = load_config()
    
def user_init():
    # Initialize the user information
    user = input('Please enter your name: ')
    
    # Initialize the data directory
    root_path = config['settings']['data_path']
    user_path = os.path.join(root_path, user)
    config['settings']['user_path'] = user_path
    os.makedirs(user_path, exist_ok=True)
    
    
def record_init():
    device_info = sd.query_devices(kind='input')
    default_device = device_info['index']
    channels = device_info['max_input_channels']
    sample_rate = int(device_info['default_samplerate'])  # Get the device's default sample rate

    # Save the recording settings to the config
    config['recording'] = {
        'device_index': default_device,
        'channels': channels,
        'samplerate': sample_rate
    }

    # Save the updated config to the config.yaml file
    with open('config.yaml', 'w') as config_file:
        yaml.dump(config, config_file)

    
def GUI_init():
    # Initialize the GUI
    root = tk.Tk()
    app = AudioPlayerApp(root)
    root.mainloop()
    

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