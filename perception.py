import os
import whisper
import json
import time
import torch
import numpy as np
import librosa
import soundfile as sf
from tensorflow.keras.models import load_model
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


class FeatureExtractor:
    """
    Reference: https://huggingface.co/spaces/Rashmiranjan28/Speech_Emotion_Recognition/tree/main
    """
    @staticmethod
    def librosa_features_extractor(file_name):
        audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
        
        # Extract MFCC features
        mfccs_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=25)
        mfccs_scaled_features = np.mean(mfccs_features.T, axis=0)

        # Extract Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y=audio)
        zcr_scaled_features = np.mean(zcr.T, axis=0)

        # Extract Chroma Features
        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        chroma_scaled_features = np.mean(chroma.T, axis=0)

        # Extract Mel Spectrogram Features
        mel = librosa.feature.melspectrogram(y=audio, sr=sample_rate)
        mel_scaled_features = np.mean(mel.T, axis=0)

        # Concatenate all features into a single array
        features = np.hstack((mfccs_scaled_features, zcr_scaled_features, chroma_scaled_features, mel_scaled_features))
        return features

class EmotionPredictor:
    def __init__(self, model_path, feature_extractor):
        self.model = load_model(model_path)
        self.feature_extractor = feature_extractor
        self.label_mapping = {0: 'angry',
                    1: 'excited',
                    2: 'fear',
                    3: 'happy',
                    4: 'neutral',
                    5: 'sad'}

    """
    Reference: https://huggingface.co/spaces/Rashmiranjan28/Speech_Emotion_Recognition/tree/main
    """
    def predict_emotions(self, audio_path, interval=3.0):
        audio_data, samplerate = sf.read(audio_path)
        duration = len(audio_data) / samplerate
        emotions = []

        for start in np.arange(0, duration, interval):
            end = start + interval
            if end > duration:
                end = duration
            segment = audio_data[int(start*samplerate):int(end*samplerate)]
            segment_path = 'segment.wav'
            sf.write(segment_path, segment, samplerate)

            feat = self.feature_extractor(segment_path)
            feat = feat.reshape(1, -1)
            predictions = self.model.predict(feat)
            predicted_label = np.argmax(predictions, axis=1)
            emotions.append((start, end, self.label_mapping[predicted_label[0]]))

            # Cleanup segment file
            os.remove(segment_path)

        return emotions
    
    
def init_librosa_model(model_path):
    global emotion_predictor
    if "emotion_predictor" not in globals():
        feature_extractor = FeatureExtractor.librosa_features_extractor
        emotion_predictor = EmotionPredictor(model_path, feature_extractor)
    return emotion_predictor


def conflict_detection(test_file_path, test_file):
    '''
    This function detects the conflict between the emotion predicted by the text and speech.
    If there is an emotion conflict, return True, else return False.
    '''
    connotation_dict = {
        "angry": "negative",
        "disgust": "negative",
        "fear": "negative",
        "fearful": "negative",
        "happy": "positive",
        "neutral": "neutral",
        "sad": "negative",
        "surprised": "positive",
        "excited": "positive"
    }
    librosa_emotion = emotion_predictor.predict_emotions(test_file_path)[0][2]
    whisper_emotion = predict_emotion(test_file, whisper_model, whisper_feature_extractor, id2label)
    print(f"Librosa emotion: {librosa_emotion}, Whisper emotion: {whisper_emotion}")

    librosa_connotation = connotation_dict[librosa_emotion]
    whisper_connotation = connotation_dict[whisper_emotion]

    # Conflict detected, use the speech emotion
    if librosa_connotation == "negative" and whisper_connotation == "positive" or librosa_connotation == "positive" and whisper_connotation == "negative":
        print(f"Conflict detected, use the speech emotion: {librosa_emotion}")
        print("Conflict detected, there is an irony. Returned True.")
        return True # There is an irony
    else:
        print(f"No conflict, use the text emotion: {whisper_emotion}")
        print("Conflict is not detected, there isn't an irony. Returned False.")
        return False
    
    
def percept():
    config = load_config()
    
    # Load audio
    audio_path = os.path.join(config["settings"]["user_path"], "recording.wav")
    audio, sr = librosa.load(audio_path, sr=16000) #sr=config["recording"]["samplerate"])
    
    # Transcripted text
    model = init_speech2text_model(device=config["settings"]["device"])
    result = model.transcribe(audio, language="en", fp16=False)
    text = result['text']
    print("Transcripted text: ", text)
    
    # Emotion detection
    whisper_model, whisper_feature_extractor, id2label = init_whisper_model()
    emotion_predictor = init_librosa_model(config["settings"]["lstm_model_path"])
    irony = conflict_detection(audio_path, audio)
    
    return text, irony


def retrieve_text():
    config = load_config()
    
    # Load audio
    audio_path = os.path.join(config["settings"]["user_path"], "recording.wav")
    audio, sr = librosa.load(audio_path, sr=16000) #sr=config["recording"]["samplerate"])
    
    # Transcripted text
    model = init_speech2text_model(device=config["settings"]["device"])
    result = model.transcribe(audio, language="en", fp16=False)
    text = result['text']
    print("Transcripted text: ", text)

    return text