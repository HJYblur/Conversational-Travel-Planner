import os
import whisper
import json
import time
import torch
import numpy as np
import librosa
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
from configure_loader import load_config


def init_speech2text_model(mode="turbo", device = 'cpu'):
    global speech2text_model
    if 'speech2text_model' not in globals():
        speech2text_model = whisper.load_model(mode, device)
    return speech2text_model


def init_whisper_model():
    global whisper_model, whisper_feature_extractor, id2label
    if "whisper_model" or "whisper_feature_extractor" or "id2label" not in globals():
        whisper_model_id = "firdhokk/speech-emotion-recognition-with-openai-whisper-large-v3"
        whisper_model = AutoModelForAudioClassification.from_pretrained(whisper_model_id)
        whisper_feature_extractor = AutoFeatureExtractor.from_pretrained(whisper_model_id, do_normalize=True)
        id2label = whisper_model.config.id2label
    return whisper_model, whisper_feature_extractor, id2label


def preprocess_audio(audio_array, feature_extractor, max_duration=30.0):
    max_length = int(feature_extractor.sampling_rate * max_duration)
    if len(audio_array) > max_length:
        audio_array = audio_array[:max_length]
    else:
        audio_array = np.pad(audio_array, (0, max_length - len(audio_array)))

    inputs = feature_extractor(
        audio_array,
        sampling_rate=feature_extractor.sampling_rate,
        max_length=max_length,
        truncation=True,
        return_tensors="pt",
    )
    return inputs


def predict_emotion(audio, model, feature_extractor, id2label, max_duration=30.0, device = "cpu"):
    inputs = preprocess_audio(audio, feature_extractor, max_duration)
    model = model.to(device)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predicted_id = torch.argmax(logits, dim=-1).item()
    predicted_label = id2label[predicted_id]

    return predicted_label

    
    
if __name__ == "__main__":
    config = load_config()
    
    # Load audio
    audio_path = os.path.join(config["settings"]["user_path"], "recording.wav")
    audio, sr = librosa.load(audio_path, sr=config["recording"]["samplerate"])
    
    # Transcripted text
    model = init_speech2text_model(device=config["settings"]["device"])
    result = model.transcribe(audio)
    print("Transcribed text:", result['text'])
    
    # Emotion detection using whisper
    whisper_model, whisper_feature_extractor, id2label = init_whisper_model()
    emotion = predict_emotion(audio, whisper_model, whisper_feature_extractor, id2label)
    print("Predicted emotion:", emotion)