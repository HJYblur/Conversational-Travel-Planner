import requests
import json
from configure_loader import load_config
import os
from pathlib import Path

# Download ollama: https://ollama.com/download
# Have ollama running in the background
# Download model: https://ollama.com/library/llama3.2 with command ollama run llama3.2
url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2:latest"
}


def build_prompt(prompt_file_path, username, dialogue, user_preferences):
    with open(prompt_file_path, "r") as file:
        prompt_text = file.read()

    user_text = f"User is {username}\n"

    if user_preferences:
        user_preferences = "User Preferences: " + ", ".join(user_preferences)

    p = prompt_text + user_text + dialogue + user_preferences
    #print(p)
    return p

def prompt(prompt_file_path, username, dialogue, user_preferences):
    data["prompt"] = build_prompt(prompt_file_path, username, dialogue, user_preferences)

    recommendation = ""
    response = requests.post(url, json=data, stream=True)
    if response.status_code == 200:
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode("utf-8")
                output = json.loads(decoded_chunk)
                recommendation += output["response"]
                #print(output["response"], end="", flush=True)
    else:
        print(f"Error: {response.status_code}")

    return recommendation

def get_entire_dialog_history(user_name):
    with (open(f"../data/{user_name}/event.json", "r") as file):
        dialogue_history = json.load(file)
        dialogue = ""
        irony_text = ""
        for entry in dialogue_history:
            if entry['irony']:
                irony_text = "Keep in mind that the user is being ironic when answering the question in the following dialogue:"
            question = f"Question: {entry['question']}"
            user_answer = f"User_answer: {entry['user_answer']}"
            dialogue += f"{irony_text}\n{question}\n{user_answer}\n"

    return dialogue

def get_last_utterances(question, user_answer):
    return f"Question: {question}\nUser_answer: {user_answer}"

def summarization(question, user_answer):
    username = load_config()['settings']['user']
    prompt_file_path = Path(r"LLM/Prompts/summarization.txt")
    dialogue = get_last_utterances(question, user_answer)
    #print(dialogue)
    return prompt(prompt_file_path, username, dialogue, "")

def response_generation(user_preferences):
    username = load_config()['settings']['user']
    prompt_file_path = Path(r"LLM/Prompts/response_generation.txt")
    dialogue = get_entire_dialog_history(username)
    #print(dialogue)
    return prompt(prompt_file_path, username, dialogue, user_preferences)
