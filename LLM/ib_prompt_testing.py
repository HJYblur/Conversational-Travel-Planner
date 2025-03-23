import requests
import json

url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2:latest"
}

# Ice Breaker Summarization

with open("Prompts/ice_breaker_summarization.txt", "r") as file:
    prompt = file.read()

user = "User is Sofia\n"

with open("../data/sofia/ice_breaker.json", "r") as file:
    dialog_history = json.load(file)

    if dialog_history:
        last_entry = dialog_history[-1] # get last two utterances
        question = f"Question: {last_entry['question']}"
        user_answer = f"User_answer: {last_entry['user_answer']}"
        last_utterances = f"{question}\n{user_answer}"
        print(last_utterances)

data["prompt"] = prompt + user + last_utterances

response = requests.post(url, json=data, stream=True)

if response.status_code == 200:
    for chunk in response.iter_lines():
        if chunk:
            decoded_chunk = chunk.decode("utf-8")
            output = json.loads(decoded_chunk)
            print(output["response"], end="", flush=True)
else:
    print(f"Error: {response.status_code}")
