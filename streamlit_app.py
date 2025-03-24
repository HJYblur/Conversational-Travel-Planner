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

        self.state = 'Start'
        self.run()
        

    def setup_session_state(self):
        if "config" not in st.session_state:
            st.session_state.config = load_config()
        if "username" not in st.session_state:
            st.session_state.username = None
        if "latest_audio" not in st.session_state:
            st.session_state.latest_audio = None

            
    def run(self):
        if not hasattr(self, 'previous_state') or self.state != self.previous_state:
            print(f"Current State: {self.state}")
            self.previous_state = self.state
        if self.state == "Start":
            self.start()
            self.state = "Idle"
        elif self.state == "Idle":
            # Step2: Record the user speech
            self.post_login_ui()
            self.record_audio()
        elif self.state == 'RecordFinish':
            # Step3: Speech to Text & Emotion Detection
            self.text, self.emotion = percept()
            self.state = 'Summary'
        elif self.state == 'Summary':
            # Step4: Summarize short-term memory from the text
            # TODO: interpolate the summary function
            self.state = 'retrieval'
        elif self.state == 'retrieval':
            # Step5: Information retrieval from long-term memory(preference)
            self.preference = retrieve(self.text)
            self.state = 'GeneratingResponce'
        elif self.state == 'GeneratingResponce':
            # Step6: Communicate with LLM to generate the response
            # TODO: interpolate the Responce Generation function
            self.agent_response = f"Generating Responce of {self.text} with {self.emotion} mood, preference: {self.preference}"
            self.state = 'Text2Speech'
        elif self.state == 'Text2Speech':
            # Step7: Convert the LLM response to speech and output to users
            # TODO: interpolate the Text2Speech function
            text2speech(self.agent_response, self.config['settings']['user_path'], 1)
            self.state = 'Idle'
        elif self.state == "Stopped":
            self.on_closing()
        
        # Schedule the next state check
        
        
        
        
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
                    st.rerun()
                else:
                    st.warning("Please enter your name to continue.")
            st.stop()


    def post_login_ui(self):
        st.subheader(f"Hi {st.session_state.username}, I'm Emma! 🌍")
        self.audio_path = os.path.join(st.session_state.config["settings"]["user_path"], "recording.wav")


    def record_audio(self):
        audio_data = st_audiorec()
        # add some spacing and informative messages
        col_info, col_space = st.columns([0.57, 0.43])
        with col_info:
            st.write('\n')  # add vertical spacer
            st.write('\n')  # add vertical spacer
            st.write('Note: Tell you how to record it 🎈')
            
        if audio_data:
            with open(self.audio_path, "wb") as f:
                f.write(audio_data)
            st.success(f"{self.CA_name} heard you!")
            self.state = "RecordFinish"
            self.run()
        
        
        


# === Main Execution ===
if __name__ == "__main__":
    app = TravelPlannerApp()
    app.run()