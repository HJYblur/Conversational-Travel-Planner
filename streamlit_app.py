import torch
import streamlit as st
from st_audiorec import st_audiorec
import os
import yaml
from configure_loader import load_config
from perception import percept
from information_retriever import retrieve
from text_to_speech import text2speech

class TravelPlannerApp:
    def __init__(self):
        self.setup_session_state()
        self.CA_name = "Emma"
        self.text = "OvO"
        self.emotion = "happy"
        self.preference = "TxT"
        self.agent_response = "Emma's response"

    def setup_session_state(self):
        if "config" not in st.session_state:
            st.session_state.config = load_config()
        if "username" not in st.session_state:
            st.session_state.username = None
        if "latest_audio" not in st.session_state:
            st.session_state.latest_audio = None
        if "state" not in st.session_state:
            st.session_state.state = "Start"

    def run(self):
        if st.session_state.state == "Start":
            self.start()
        elif st.session_state.state == "Idle":
            self.post_login_ui()
            self.record_audio()
        elif st.session_state.state == 'RecordFinish':
            self.text, self.emotion = percept()
            print("percep")
            st.session_state.state = 'Summary'
            
        elif st.session_state.state == 'Summary':
            self.preference = retrieve(self.text)
            print("retrieve")
            st.session_state.state = 'GeneratingResponce'
            
        elif st.session_state.state == 'GeneratingResponce':
            self.agent_response = f"Generating Response of {self.text} with {self.emotion} mood, preference: {self.preference}"
            st.session_state.state = 'Text2Speech'
            
        elif st.session_state.state == 'Text2Speech':
            text2speech(self.agent_response, st.session_state.config['settings']['user_path'], 1)
            print("text2speech")
            st.session_state.state = 'Idle'
            
        elif st.session_state.state == "Stopped":
            st.stop()

    def start(self):
        st.title(f"👋 Meet {self.CA_name}, your Conversational Travel Planner")
        if st.session_state.username is None:
            user = st.text_input("Please enter your name:")
            if st.button("Start"):
                if user:
                    st.session_state.username = user
                    user_path = os.path.join(st.session_state.config["settings"]["data_path"], user)
                    os.makedirs(user_path, exist_ok=True)
                    st.session_state.config["settings"]["user"] = user
                    st.session_state.config["settings"]["user_path"] = user_path
                    with open("config.yaml", "w") as f:
                        yaml.dump(st.session_state.config, f)
                    st.success(f"Welcome, {user}!")
                    st.session_state.state = "Idle"
                    
                else:
                    st.warning("Please enter your name to continue.")
            st.stop()

    def post_login_ui(self):
        st.subheader(f"Hi {st.session_state.username}, I'm {self.CA_name}! 🌍")
        self.audio_path = os.path.join(st.session_state.config["settings"]["user_path"], "recording.wav")

    def record_audio(self):
        audio_data = st_audiorec()
        if audio_data:
            with open(self.audio_path, "wb") as f:
                f.write(audio_data)
            st.success(f"{self.CA_name} heard you!")
            st.session_state.state = "RecordFinish"
            

# === Main Execution ===
if __name__ == "__main__":
    app = TravelPlannerApp()
    app.run()