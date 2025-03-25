import requests
import json
from configure_loader import load_config

# Download ollama: https://ollama.com/download
# Have ollama running in the background
# Download model: https://ollama.com/library/llama3.2 with command ollama run llama3.2
url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2:latest"
}


def prompt(prompt_file_path, user, question, user_answer, emotion="", user_preferances=""):

    user_name = load_config()['settings']['user']
    user = f"User is {user_name}"

    with open(prompt_file_path, "r") as file:
        prompt = file.read()
    dialog = f"Dialog history:\nQuestion: {question}\nUser_answer: {user_answer}\n" 

    if user_preferances:
        data["prompt"] = prompt + user_preferances + user + dialog
    else:
        data["prompt"] = prompt + user + dialog

    response = requests.post(url, json=data, stream=True)
    if response.status_code == 200:
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode("utf-8")
                output = json.loads(decoded_chunk)
                print(output["response"], end="", flush=True) 
    else:
        print(f"Error: {response.status_code}")

    return response


def summarization(question, user_answer, emotion):
    prompt_file_path = "Prompts/ice_breaker_summarization.txt"
    
    prompt(prompt_file_path, question, user_answer, emotion)


def memory_query_generation(question, user_answer, emotion):
    prompt_file_path = "Prompts/memory_query_generation.txt"

    prompt(prompt_file_path, question, user_answer, emotion)


def response_generation(question, user_answer, emotion, user_preferances):
    prompt_file_path = "Prompts/response_generation.txt"
    
    prompt(prompt_file_path, question, user_answer, emotion, user_preferances)

