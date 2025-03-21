import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import pygame

class ConversationalAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversational Travel Planner")

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=15)
        self.chat_area.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.user_input = tk.Entry(root, width=40)
        self.user_input.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

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
        


class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversational Travel Planner")

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=15)
        self.chat_area.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.user_input = tk.Entry(root, width=40)
        self.user_input.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Create buttons for opening, playing, pausing, and resuming audio files
        self.open_button = tk.Button(root, text="Open Audio File", command=self.open_audio)
        self.play_button = tk.Button(root, text="Play", state=tk.DISABLED, command=self.play_audio)
        self.pause_button = tk.Button(root, text="Pause", state=tk.DISABLED, command=self.pause_audio)
        self.resume_button = tk.Button(root, text="Resume", state=tk.DISABLED, command=self.resume_audio)

        self.open_button.pack(pady=10)
        self.play_button.pack()
        self.pause_button.pack()
        self.resume_button.pack()

        # Initialize pygame
        pygame.mixer.init()

        # Register a callback to stop audio when the window is closed
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize playback state
        self.paused = False

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

    def pause_audio(self):
        pygame.mixer.music.pause()
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
        self.paused = True

    def resume_audio(self):
        pygame.mixer.music.unpause()
        self.resume_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.paused = False

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

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayerApp(root)
    root.mainloop()
