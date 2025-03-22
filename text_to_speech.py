import pyttsx3

"""
Library ref: https://pypi.org/project/pyttsx3/
Advantanges of pyttsx3:
1. It works offline.
2. It supports multiple TTS engines, including Sapi5, nsss, and espeak.
"""

def convert_text_to_speech(text, userID, turnID):
    engine = pyttsx3.init()
    engine.say(text)
    engine.save_to_file(text, f"text-to-speech-outputs/output_{userID}_{turnID}.wav")
    engine.runAndWait()


if __name__ == "__main__":
    text = "Hello, how are you?"
    userID = "sofia"
    turnID = 1
    convert_text_to_speech(text, userID, turnID)