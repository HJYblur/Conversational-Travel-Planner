import requests
import json

# Download ollama: https://ollama.com/download
# Have ollama running in the background
# Download model: https://ollama.com/library/llama3.2 with command ollama run llama3.2
url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2:latest"
}

# loop here
data["prompt"] = "Summarize the following utterances from the perspective of the user (in third-person): CA: Hi Sofia! Lovely to see you again. As I remember from our previous conversation you love to travel! Would you like something similar to your road trip to the USA, or a more relaxed vacation close to nature? User: Hmm. Maybe not a road trip. I don't want to spend that much time in a car. To be honest, I would like to go somewhere warm. A place where I can truly relax and recover."
response = requests.post(url, json=data, stream=True)

if response.status_code == 200:
    for chunk in response.iter_lines():
        if chunk:
            decoded_chunk = chunk.decode("utf-8")
            output = json.loads(decoded_chunk)
            print(output["response"], end="", flush=True)
else:
    print(f"Error: {response.status_code}")
