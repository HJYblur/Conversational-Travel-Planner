import requests
import json

# Download ollama: https://ollama.com/download
# Have ollama running in the background
# Download model: https://ollama.com/library/llama3.2 with command ollama run llama3.2
url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2:latest"
}

### memory_query_generation
# with open("Prompts/memory_query_generation.txt", "r") as file:
#     prompt = file.read()
# # Only the most recent event
# with open("../data/sofia/event.json", "r") as file:
#     dialog_history = json.load(file)
#     dialog_new = dialog_history[-2]
#     question = "Question: " + dialog_new["question"]
#     user_answer = "User_answer: " + dialog_new["user_answer"]
#     dialog = f"Dialog history:\n{question}\n{user_answer}\n" 
# user = "User is Sofia\n\n"
# data["prompt"] = prompt + user + dialog


### response_generation

with open("Prompts/response_generation.txt", "r") as file:
    prompt = file.read()

user_preferances = '''
The user's preferences:
- Loves to travel.
- Top three travels were to the USA (road trip), South Africa (visited friend), and Paris (Olympics).
- Likes to travel in nature.
'''

user = "User is Sofia\n"

# Several events
with open("../data/sofia/event.json", "r") as file:
    dialog_history = json.load(file)
    dialog = ""
    for entry in dialog_history:
        question = f"Question: {entry['question']}"
        user_answer = f"User_answer: {entry['user_answer']}"
        dialog += f"{question}\n{user_answer}\n"

# loop here
data["prompt"] = prompt +  user_preferances + user + dialog

response = requests.post(url, json=data, stream=True)

if response.status_code == 200:
    for chunk in response.iter_lines():
        if chunk:
            decoded_chunk = chunk.decode("utf-8")
            output = json.loads(decoded_chunk)
            print(output["response"], end="", flush=True) 
else:
    print(f"Error: {response.status_code}")
