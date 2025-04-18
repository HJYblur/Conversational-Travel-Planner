import pyttsx3
import re
import time

"""
Library ref: https://pypi.org/project/pyttsx3/
Advantanges of pyttsx3:
1. It works offline.
2. It supports multiple TTS engines, including Sapi5, nsss, and espeak.
"""

def preprocess_text(agent_text):
    '''
        Method for splitting the agent text into sentence parts 
        by using the punctuation marks: '.', '!', '?', and ','.
    '''
    sentence_parts = re.split(r'([.!?,])', agent_text)
    sentences = [sentence_parts[i] + sentence_parts[i+1] for i in range(0, len(sentence_parts)-1, 2)]
    return sentences
    

def text2speech(text):
    '''
        Text-to-speech conversion using pyttsx3 library.
    '''
    engine = pyttsx3.init()

    # Set voice properties
    engine.setProperty('rate', 180) # Make the speech slower (from 200 to 180)

    sentences = preprocess_text(text)
    
    for sentence_part in sentences:
        # Say each sentence part one by one
        # Wait for 0.5 seconds after each sentence part
        # for ensuring the conversation is more natural and human-like
        engine.say(sentence_part) 
        engine.runAndWait()
        time.sleep(0.5)  
