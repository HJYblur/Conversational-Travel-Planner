import yaml
import tkinter as tk
import sounddevice as sd
import torch
from gui import AudioPlayerApp
from configure_loader import load_config
config = load_config()
    
    
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
    

def perception_init():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config["settings"]["device"] = str(device)

    with open('config.yaml', 'w') as config_file:
        yaml.dump(config, config_file)