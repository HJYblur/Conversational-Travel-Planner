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


def prompt(prompt_file_path, question, user_answer, irony, user_preferences=""):

    with open(prompt_file_path, "r") as file:
        prompt_text = file.read()

    user_name = load_config()['settings']['user']
    user_text = f"User is {user_name}\n"

    irony_text = ""
    if irony:
        irony_text = "Keep in mind that the user is being ironic when answering the question in the following dialog:\n"
    
    dialog_history = f"Dialog history:\nQuestion: {question}\nUser_answer: {user_answer}\n" 

    if user_preferences:
        user_preferences = "User Preferences: " + ", ".join(user_preferences)
        data["prompt"] = prompt_text + user_text + irony_text + dialog_history + user_preferences
    else:
        data["prompt"] = prompt_text + user_text + irony_text + dialog_history

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


def summarization(question, user_answer, irony):
    prompt_file_path = Path(r"LLM/Prompts/summarization.txt")

    return prompt(prompt_file_path, question, user_answer, irony)


def memory_query_generation(question, user_answer, irony):
    prompt_file_path = Path(r"LLM/Prompts/memory_query_generation.txt")

    return prompt(prompt_file_path, question, user_answer, irony)


def response_generation(question, user_answer, irony, user_preferences):
    prompt_file_path = Path(r"LLM/Prompts/response_generation.txt")
    
    return prompt(prompt_file_path, question, user_answer, irony, user_preferences)

