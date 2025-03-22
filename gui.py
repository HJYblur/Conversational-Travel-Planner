import tkinter as tk
from tkinter import scrolledtext, simpledialog
import os
import sounddevice as sd
import wavio
import numpy as np
import threading
from scipy.io.wavfile import write
from configure_loader import load_config

class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversational Travel Planner")
        self.center_window()
        self.config = load_config()

        self.planner_name_label = tk.Label(root, text="Alice", font=("Helvetica", 32))
        self.planner_name_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Create a display bar for displaying different text/animation according to the input
        self.display_bar = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=3)
        self.display_bar.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        # Create a frame for the audio controls
        audio_frame = tk.Frame(root)
        audio_frame.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

        self.start_button = tk.Button(audio_frame, text="Start Recording", command=self.start_recording)
        self.end_button = tk.Button(audio_frame, text="End Recording", command=self.stop_recording, state=tk.DISABLED)
        
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        self.end_button.grid(row=0, column=1, padx=5, pady=5)

        # Register a callback to stop audio when the window is closed
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize recording state
        self.recording = False
        self.audio_data = []
        
        # Initialize GUI display
        self.start()


    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width() * 2
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
            
    def start(self):
        user = simpledialog.askstring("User Initialization", "Please enter your name:")
        
        if user:
            # Initialize the data directory
            root_path = self.config['settings']['data_path']
            user_path = os.path.join(root_path, user)
            self.config['settings']['user_path'] = user_path
            os.makedirs(user_path, exist_ok=True)
            
            self.display(f"Hello {user}, welcome to the travel recommendation agent!\n")
        else:
            # If the user cancels the input dialog, close the application
            self.root.destroy()

    def start_recording(self):
        if not self.recording:
            self.audio_data = []
            self.recording = True
            print(f"Recording started... (Device: {self.config['recording']['device_index']}, Channels: {self.config['recording']['channels']})")

            def callback(indata, frames, time, status):
                if status:
                    print(status)
                if self.recording:
                    self.audio_data.append(indata.copy())

            def record_audio():
                with sd.InputStream(samplerate=self.config['recording']['samplerate'], channels=self.config['recording']['channels'], device=self.config['recording']['device_index'], callback=callback):
                    while self.recording:
                        sd.sleep(100)

            threading.Thread(target=record_audio, daemon=True).start()
            self.start_button.config(state=tk.DISABLED)
            self.end_button.config(state=tk.NORMAL)
            self.display("Recording started...\n", True)
            

    def stop_recording(self):
        self.recording = False
        print("Recording stopped. Saving file...")

        if self.audio_data:
            audio_array = np.concatenate(self.audio_data, axis=0)  # Convert list to NumPy array
            audio_path = os.path.join(self.config["settings"]["user_path"], "recording.wav")
            wavio.write(audio_path, audio_array, self.config['recording']['samplerate'], sampwidth=2)
            print(f"Saved as {audio_path}")
            self.start_button.config(state=tk.NORMAL)
            self.end_button.config(state=tk.DISABLED)
            self.display(f"Recording saved to {audio_path}\n", True)
            
            
    def display(self, str = str, rewrite = True):
        self.display_bar.config(state='normal')
        if rewrite:
            self.display_bar.delete(1.0, tk.END)
        self.display_bar.insert(tk.END, str, "center")
        self.display_bar.config(state='disabled')
            
            
    def on_closing(self):
        self.root.destroy()