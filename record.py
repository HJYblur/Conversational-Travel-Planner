import tkinter as tk
import sounddevice as sd
import wavio
import numpy as np
import threading

# Automatically get the default microphone
device_info = sd.query_devices(kind='input')
default_device = device_info['index']
channels = device_info['max_input_channels']

# Recording settings
samplerate = int(device_info['default_samplerate'])  # Get the device's default sample rate
filename = "recording.wav"

recording = False
audio_data = []

def record_audio():
    global recording, audio_data
    audio_data = []
    recording = True
    print(f"Recording started... (Device: {default_device}, Channels: {channels})")

    def callback(indata, frames, time, status):
        if status:
            print(status)
        if recording:
            audio_data.append(indata.copy())

    with sd.InputStream(samplerate=samplerate, channels=channels, device=default_device, callback=callback):
        while recording:
            sd.sleep(100)

def start_recording():
    global recording
    if not recording:
        threading.Thread(target=record_audio, daemon=True).start()

def stop_recording():
    global recording
    recording = False
    print("Recording stopped. Saving file...")

    if audio_data:
        audio_array = np.concatenate(audio_data, axis=0)  # Convert list to NumPy array
        wavio.write(filename, audio_array, samplerate, sampwidth=2)
        print(f"Saved as {filename}")

# Tkinter UI
root = tk.Tk()
root.title("Simple Audio Recorder")

start_button = tk.Button(root, text="Start Recording", command=start_recording, width=20)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, width=20)
stop_button.pack(pady=10)

root.mainloop()