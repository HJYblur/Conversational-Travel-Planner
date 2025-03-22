import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import os
import pygame
import record
from scipy.io.wavfile import write
from configure_loader import load_config


class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversational Travel Planner")
        self.config = load_config()

        # Create a frame for the chat area and user input
        chat_frame = tk.Frame(root)
        chat_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.chat_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state='disabled', width=50, height=15)
        self.chat_area.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.user_input = tk.Entry(chat_frame, width=40)
        self.user_input.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(chat_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Create a frame for the audio controls
        audio_frame = tk.Frame(root)
        audio_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.record_button = tk.Button(audio_frame, text = "Record user input", command=self.record_audio)
        self.open_button = tk.Button(audio_frame, text="Open Audio File", command=self.open_audio)
        self.play_button = tk.Button(audio_frame, text="Play", state=tk.DISABLED, command=self.play_audio)
        
        self.record_button.grid(row=0, column=0, padx=5, pady=5)
        self.open_button.grid(row=0, column=1, padx=5, pady=5)
        self.play_button.grid(row=0, column=2, padx=5, pady=5)

        # Initialize pygame
        pygame.mixer.init()

        # Register a callback to stop audio when the window is closed
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize playback state
        self.paused = False
    
    
    def record_audio(self):
        freq = self.config["settings"]["freq"]
        duration = self.config["settings"]["duration"]
        
        try:
            recording = sd.rec(int(duration * freq), samplerate=freq, channels=4)
            sd.wait()  # Wait until recording is finished
            audio_path = os.path.join(self.config["settings"]["user_path"], "recording.wav")
            write(audio_path, freq, recording)
            print(f"Recording saved to {audio_path}")
        except Exception as e:
            print(f"An error occurred while recording audio: {e}")



    def open_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path:
            self.audio_file = file_path
            self.play_button.config(state=tk.NORMAL)
            

    def play_audio(self):
        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play()
        self.play_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        

    def on_closing(self):
        # Check if audio is currently playing
        if pygame.mixer.music.get_busy():
            # Stop audio playback before closing the application
            pygame.mixer.music.stop()
        self.root.destroy()


    def send_message(self):
        user_message = self.user_input.get()
        if user_message.strip():
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, "User: " + user_message + "\n")
            self.chat_area.config(state='disabled')
            self.user_input.delete(0, tk.END)
            self.respond(user_message)
        return user_message


    def respond(self, user_message):
        if user_message:
            agent_response = user_message
        else:
            agent_response = "Agent: I am here to help you."
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, agent_response + "\n")
        self.chat_area.config(state='disabled')
        