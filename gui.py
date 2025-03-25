import tkinter as tk
from tkinter import scrolledtext, simpledialog
import os
import yaml
import sounddevice as sd
import wavio
import numpy as np
import threading
from configure_loader import load_config
from perception import percept
from information_retriever import retrieve
from text_to_speech import text2speech
from LLM.prompting import memory_query_generation, response_generation, summarization

class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversational Travel Planner")
        self.config = load_config()
        self.CA_name = "Emma"
        self.center_window()

        # Define styling options
        title_font = ("SF pro", 32, "bold")
        text_font = ("SF pro", 16)
        btn_font = ("SF pro", 12, "bold")

        # === Title Section ===
        title_frame = tk.Frame(root, pady=10)
        title_frame.pack(fill="x")

        self.planner_name_label = tk.Label(title_frame, text=self.CA_name, font=title_font, fg="#3B3B98")
        self.planner_name_label.pack()

        # === Display Bar (Text) ===
        display_frame = tk.Frame(root, pady=10)
        display_frame.pack(fill="x", padx=20)

        self.display_bar = tk.Text(
            display_frame, wrap=tk.WORD, state="disabled", 
            width=60, height=10, font=text_font, bg="#F8F8F8"
        )
        self.display_bar.tag_configure("center", justify='center')
        self.display_bar.pack(fill="both", expand=True)

        # === Audio Control Buttons ===
        audio_frame = tk.Frame(root, pady=10)
        audio_frame.pack()

        self.start_button = tk.Button(audio_frame, text="Start Recording", font=btn_font, command=self.start_recording, bg="#4CAF50")
        self.end_button = tk.Button(audio_frame, text="End Recording", font=btn_font, command=self.stop_recording, bg="#F44336", state=tk.DISABLED)

        self.start_button.grid(row=0, column=0, padx=10, pady=5)
        self.end_button.grid(row=0, column=1, padx=10, pady=5)

        # Closing Protocol
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize Recording State
        self.recording = False
        self.audio_data = []
        self.text = "OvO"
        self.emotion = "happy"
        self.preference = "TxT"
        self.agent_response = "Emma's response"

        # Initialize State Machine
        self.state = "Start"
        self.update()
        

    def update(self):
        if not hasattr(self, 'previous_state') or self.state != self.previous_state:
            print(f"Current State: {self.state}")
            self.previous_state = self.state
        if self.state == "Start":
            self.start()
            self.state = "Idle"
        elif self.state == "Idle":
        # Step2: Record the user speech
            if self.start_button.config('state')[-1] == tk.DISABLED:
                self.state = "Recording"
                self.display(f"{self.CA_name} is listening!")
        elif self.state == "Recording":
            # Wait for the user to click the "End Recording" button
            if self.end_button.config('state')[-1] == tk.DISABLED:
                self.display(f"Ahh, {self.CA_name} get you :)")
                self.state = 'RecordFinish'
        elif self.state == 'RecordFinish':
            # Step3: Speech to Text & Emotion Detection
            self.display(f"{self.CA_name} is thinking!")
            self.text, self.emotion = percept()
            self.state = 'Summary'
        elif self.state == 'Summary':
            # Step4: Summarize short-term memory from the text
            # TODO: interpolate the summary function
            # summarization("TODO", self.text, self.emotion) # TODO add CA question
            self.display("Summarizing the text now\n")
            self.state = 'retrieval'
        elif self.state == 'retrieval':
            # Step5: Information retrieval from long-term memory(preference)
            question = self.agent_response
            memory_query = memory_query_generation(question, self.text, self.emotion)
            self.preference = retrieve(memory_query)
            self.state = 'GeneratingResponse'
        elif self.state == 'GeneratingResponse':
            # Step6: Communicate with LLM to generate the response
            # TODO: interpolate the Response Generation function
            question = self.agent_response
            self.agent_response = response_generation(question, self.text, self.emotion, self.preference)
            self.display(self.agent_response)
            self.state = 'Text2Speech'
        elif self.state == 'Text2Speech':
            # Step7: Convert the LLM response to speech and output to users
            # TODO: interpolate the Text2Speech function
            text2speech(self.agent_response)
            self.state = 'Idle'
        elif self.state == "Stopped":
            self.on_closing()
        
        # Schedule the next state check
        self.root.after(100, self.update)
        
        
            
    def start(self):
        user = simpledialog.askstring("User Initialization", "Please enter your name:")
        
        if user:
            # Initialize the data directory
            root_path = self.config['settings']['data_path']
            user_path = os.path.join(root_path, user)
            self.config["settings"]['user'] = user
            self.config['settings']['user_path'] = user_path
            with open('config.yaml', 'w') as config_file:
                yaml.dump(self.config, config_file)
            os.makedirs(user_path, exist_ok=True)

            self.agent_response = f"Hello {user}, welcome to the travel recommendation agent!\n"
            self.display(self.agent_response)
            text2speech(self.agent_response)
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
            # Stop recoding the file
            audio_array = np.concatenate(self.audio_data, axis=0)  # Convert list to NumPy array
            audio_path = os.path.join(self.config["settings"]["user_path"], "recording.wav")
            wavio.write(audio_path, audio_array, self.config['recording']['samplerate'], sampwidth=2)
            print(f"Saved as {audio_path}")
            self.start_button.config(state=tk.NORMAL)
            self.end_button.config(state=tk.DISABLED)
            # self.display(f"Recording saved to {audio_path}\n", True)
            
            
    def display(self, text="", rewrite=True):
        """ Updates the display bar with new text """
        self.display_bar.config(state="normal")
        if rewrite:
            self.display_bar.delete(1.0, tk.END)
        self.display_bar.insert(tk.END, text + "\n", "center")
        self.display_bar.config(state="disabled")


    def center_window(self):
        """ Centers the window on the screen """
        self.root.update_idletasks()
        width = 600  # Set a fixed width
        height = 400  # Set a fixed height
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        
    def on_closing(self):
        self.root.destroy()