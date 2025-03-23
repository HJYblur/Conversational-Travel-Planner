import whisper
import torch
import os
import json
import time
import librosa
import numpy as np
import soundfile as sf

# Load Whisper model
device = "cuda" if torch.cuda.is_available() else "cpu"
model_turbo = whisper.load_model("turbo", device)

def speech_to_text(audio_path):
    """
    Convert speech to text using the Whisper model.
    
    Parameters:
    audio_path (str): Path to the audio file.
    
    Returns:
    str: Transcribed text.
    """
    # Load audio file
    audio, sr = librosa.load(audio_path, sr=None)
    
    # Save the audio file in the format required by Whisper
    temp_audio_path = "temp_audio.wav"
    sf.write(temp_audio_path, audio, sr)
    
    # Transcribe audio to text
    result = model_turbo.transcribe(temp_audio_path)
    
    # Remove the temporary audio file
    os.remove(temp_audio_path)
    
    return result['text']

# Example usage
if __name__ == "__main__":
    audio_path = "path_to_your_audio_file.wav"
    text = speech_to_text(audio_path)
    print("Transcribed text:", text)