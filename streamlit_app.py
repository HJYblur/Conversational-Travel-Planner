import streamlit as st
import sounddevice as sd
import numpy as np
import wavio
import os
import yaml
from configure_loader import load_config

# GLOBAL recording buffer (safe for callback)
recording_buffer = []

class TravelPlannerApp:
    def __init__(self):
        self.setup_session_state()
        self.samplerate = st.session_state.config["recording"]["samplerate"]
        self.channels = st.session_state.config["recording"]["channels"]
        self.device_index = st.session_state.config["recording"]["device_index"]
        self.audio_path = None
        self.stream = None

    def setup_session_state(self):
        if "config" not in st.session_state:
            st.session_state.config = load_config()
        if "username" not in st.session_state:
            st.session_state.username = None
        if "is_recording" not in st.session_state:
            st.session_state.is_recording = False
        if "latest_audio" not in st.session_state:
            st.session_state.latest_audio = None

    def ask_username(self):
        st.title("👋 Meet Emma, your Conversational Travel Planner")
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
                    st.rerun()
                else:
                    st.warning("Please enter your name to continue.")
            st.stop()

    def post_login_ui(self):
        st.subheader(f"Hi {st.session_state.username}, I'm Emma! 🌍")
        self.audio_path = os.path.join(st.session_state.config["settings"]["user_path"], "recording.wav")

    def start_recording(self):
        global recording_buffer
        recording_buffer = []
        st.session_state.is_recording = True

        def callback(indata, frames, time, status):
            if status:
                print(status)
            recording_buffer.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            device=self.device_index,
            callback=callback,
        )
        self.stream.start()
        st.session_state.stream = self.stream
        st.toast("🎙️ Emma is listening...")

    def stop_recording(self):
        global recording_buffer
        if "stream" in st.session_state and st.session_state.stream:
            st.session_state.stream.stop()
            st.session_state.stream.close()
            st.session_state.is_recording = False

            if recording_buffer:
                audio_array = np.concatenate(recording_buffer, axis=0)
                wavio.write(self.audio_path, audio_array, self.samplerate, sampwidth=2)
                st.session_state.latest_audio = self.audio_path
                st.success(f"Recording saved to {self.audio_path}")
                recording_buffer = []
            else:
                st.warning("No audio data recorded.")
        else:
            st.warning("Recording was not active.")

    def ui_controls(self):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Recording", disabled=st.session_state.is_recording):
                self.start_recording()
        with col2:
            if st.button("Stop Recording", disabled=not st.session_state.is_recording):
                self.stop_recording()

    def playback(self):
        if st.session_state.latest_audio and os.path.exists(st.session_state.latest_audio):
            st.audio(st.session_state.latest_audio)

    def run(self):
        self.ask_username()
        self.post_login_ui()
        self.ui_controls()
        self.playback()


# === Main Execution ===
if __name__ == "__main__":
    app = TravelPlannerApp()
    app.run()
