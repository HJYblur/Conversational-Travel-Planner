import tkinter as tk
from tkinter import scrolledtext, simpledialog
import os
import yaml
import sounddevice as sd
import wavio
import numpy as np
import threading
from configure_loader import load_config
from utils import init_json, append_to_json
from perception import percept, speech2text
from information_retriever import retrieve
from text_to_speech import text2speech
from LLM.prompting import response_generation, summarization

class AudioPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversational Travel Planner")
        self.config = load_config()
        self.CA_name = "TAP"
        self.center_window()
        self.condition = 0 # 0: ice_breaker, 1: with memory, 2: without memory
        # self.session_counter = 0 # 1: session 1, 2: session 2
        self.end_experiment = False # When True experiment will end after the following round

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

        self.start_button = tk.Button(audio_frame, text="Start Talking", font=btn_font, command=self.start_recording, bg="#4CAF50")
        self.end_button = tk.Button(audio_frame, text="End Talking", font=btn_font, command=self.stop_recording, bg="#F44336", state=tk.DISABLED)
        self.end_session_button = tk.Button(audio_frame, text="End Session", font=btn_font, command=self.next_session, bg="#FF9800")

        audio_frame.columnconfigure(0, weight=1)
        audio_frame.columnconfigure(1, weight=1)
        audio_frame.columnconfigure(2, weight=1)

        self.start_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.end_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.end_session_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # Closing Protocol
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize Recording State
        self.recording = False
        self.audio_data = []
        self.text = "OvO"
        self.irony = False
        self.summary = "Summary"
        self.ice_breaker = ""
        self.agent_response = "Emma's response"
        self.num_turns = 0 
        self.max_turns = 3 
        self.event_counter = 0
        self.final_response = False
        self.icebreaker_question_counter = 0

        # Initialize State Machine
        self.state = "Start"
        self.update()

    def update(self):
        if not hasattr(self, 'previous_state') or self.state != self.previous_state:
            print(f"Current State: {self.state}")
            self.previous_state = self.state
        if self.state == "Start":
            self.start()
            self.state = "IceBreaker"
        elif self.state == "IceBreaker":
            # self.display(self.icebreaker_questions[self.icebreaker_question_counter]) #///before///
            self.agent_response = self.icebreaker_questions[self.icebreaker_question_counter] 
            self.display(self.agent_response)
            self.display_bar.update_idletasks()  
            text2speech(self.icebreaker_questions[self.icebreaker_question_counter])
            self.state = "Idle"
        elif self.state == "Idle":
            # Step2: Record the user speech
            if self.start_button.config('state')[-1] == tk.DISABLED:
                self.state = "Recording"
                # self.display(f"{self.CA_name} is listening!") # before
                self.display(self.agent_response)
                self.display_bar.update_idletasks()
        elif self.state == "Recording":
            # Wait for the user to click the "End Recording" button
            if self.end_button.config('state')[-1] == tk.DISABLED:
                self.display(f"Gotcha, give me a moment to think that through :)")
                self.display_bar.update_idletasks()
                self.state = 'RecordFinish'
        elif self.state == 'RecordFinish':
            # Step3: Speech to Text & Emotion Detection
            self.display(f"{self.CA_name} is thinking!")
            self.display_bar.update_idletasks()
            # If in ice_breaker session, go back to IceBreaker
            if self.condition == 0:
                self.text = speech2text()
                self.summary = summarization(self.icebreaker_questions[self.icebreaker_question_counter], self.text)
                append_to_json(self.summary, self.icebreaker_question_counter)
                self.icebreaker_question_counter += 1   
                if self.icebreaker_question_counter == self.config['settings']['icebreaker_question_count']:
                    self.state = 'ConditionChange'
                else:
                    self.state = 'IceBreaker'
            else:
                self.text, self.irony = percept()
                self.state = 'Summary'
        elif self.state == 'Summary':
            # Step4: Summarize short-term memory from the text
            self.display(f"{self.CA_name} is summarizing your idea now :)\n")
            self.display_bar.update_idletasks()
            question = self.agent_response
            self.summary = summarization(question, self.text)
            append_to_json(self.summary, self.event_counter, self.irony, "event.json")
            self.event_counter += 1
            if self.condition == 1: # with memory
                self.state = 'retrieval' 
            else: # without memory
                self.state = 'GeneratingResponse'
        elif self.state == 'retrieval':
            # Step5: Information retrieval from long-term memory
            self.ice_breaker = retrieve(self.summary, "ice_breaker") # memory_type = 'ice_breaker' or 'event'
            print(f"In 'with memory' condition, the retrieved ice_breaker: {self.ice_breaker}")
            
            self.event = retrieve(self.summary, "event")
            self.state = 'GeneratingResponse'
        elif self.state == 'GeneratingResponse':
            # Keep track of number of turns
            if self.condition != 0: 
                self.num_turns += 1
                if self.num_turns == self.max_turns:
                    self.final_response = True
            # Step6: Communicate with LLM to generate the response
            self.agent_response = response_generation(self.ice_breaker, self.final_response)
            self.display(self.agent_response)
            self.display_bar.update_idletasks()  
            self.state = 'Text2Speech'
        elif self.state == 'Text2Speech':
            # Step7: Convert the LLM response to speech and output to users
            self.display(self.agent_response)  
            self.display_bar.update_idletasks()  
            text2speech(self.agent_response)
            self.state = 'Idle'
            # If final response, change condition
            if self.final_response: # If yes, change condition
                self.next_session()
        elif self.state == 'ConditionChange':
            # Convert from ice-breaker to the first stage
            self.condition = int(self.config['custom']['memory_condition'])
            print(f"We are continuing with condition {self.condition} now.")

            self.agent_response = "Let's start with session 1.\nNow that I got to know you more, I want to help you plan your next trip. First off, during which season do you prefer to travel and with whom?"
            self.display(self.agent_response)
            self.display_bar.update_idletasks()  
            text2speech(self.agent_response)
            self.state = 'Idle'
        elif self.state == "Stopped":
            self.on_closing()

        # Schedule the next state check
        self.root.after(100, self.update)

    def start(self):
        # Initialize the with/without episodic memory
        episodic_type = simpledialog.askstring("Set episodic type", "** ONLY controlled by researcher **")
        if episodic_type:
            self.config["custom"]["memory_condition"] = episodic_type
            with open('config.yaml', 'w') as config_file:
                yaml.dump(self.config, config_file)

        self.user = simpledialog.askstring("User Initialization", "Please enter your name:")

        if self.user:
            # Initialize the data directory in configuration
            root_path = './data'
            user_path = os.path.join(root_path, self.user)
            self.config["settings"]['user'] = self.user
            self.config['settings']['user_path'] = user_path
            with open('config.yaml', 'w') as config_file:
                yaml.dump(self.config, config_file)
            os.makedirs(user_path, exist_ok=True)

            # Initialize the ice_breaker.json and event.json files in the user folder
            init_json("ice_breaker.json")
            init_json("event.json") 

            self.agent_response = f"Hello {self.user}, I'm {self.CA_name}, your travel recommendation agent!\n"
            self.display(self.agent_response)
            self.display_bar.update_idletasks() 
            text2speech(self.agent_response)
            
            # Initialize the icebreaker questions
            self.init_icebreaker()
        else:
            # If the user cancels the input dialog, close the application
            self.root.destroy()
            
    def next_session(self):
        if self.condition == 0:
            print("Icebreaker session cannot be terminated.")
            return
        
        if self.end_experiment:
            self.display("Thank you for participating in the experiment! :)")
            text2speech("Thank you for participating in the experiment!")
            # self.state = "Stopped"
            # self.update()
        else:
            self.condition = 2 if self.condition == 1 else 1

            transition_message = "This is the end of Session 1. \n Before we start the next session, please fill in the questionnaire :)\n When you are ready, please click the 'Start Talking' button to begin the next session and tell me during which season do you prefer to travel and with whom?"
            self.agent_response = transition_message
            self.display(transition_message)
            self.display_bar.update_idletasks() 
            text2speech(transition_message)

            # Clear event file
            init_json("event.json") 

            self.end_experiment = True
            self.final_response = False
            self.num_turns = 0
            self.ice_breaker = ""
            self.state = "Idle"
            self.update()

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
            
    def init_icebreaker(self):
        self.icebreaker_questions = [
            "Today, I am here to help you plan your next great travel adventure. But first, let's get to know each other a little! How old are you and do you work, study, or a bit of both?",
            "That's great! I bet that keeps you busy. When you're on vacation, what's your favorite way to spend your days? Are you more into sightseeing, adventure, relaxation, food, or something else?",
            "That sounds like the perfect way to spend a trip! And speaking of trips - what's your go-to mode of transportation when you travel? Planes, trains, road trips? Any you prefer to avoid?",
            "Nice! If you had to pick your favorite trip so far, which one stands out and what did you enjoy most about that trip?",
            "That sounds amazing! What about your most recent trip?",
            "Thank you for sharing! Anything else I should know? Otherwise, lets get started!",
        ]

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