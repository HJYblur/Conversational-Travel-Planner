import requests
import json
from configure_loader import load_config
from pathlib import Path

# Download ollama: https://ollama.com/download
# Have ollama running in the background
# Download model: https://ollama.com/library/llama3.2 with command ollama run llama3.2
url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2:latest"
}


def build_prompt(prompt_file_path, username, dialogue, user_preferences, final_response_bool):
    with open(prompt_file_path, "r") as file:
        prompt_text = file.read()
    user_text = f"User is {username}\n"

    final_response = ""
    if final_response_bool:
        final_response = "This is your final travel recommendation to the user, wrap up accordingly."
    else:
        prompt_text += "- Make sure you **finish by asking a question** to the user to keep the conversation going.\n"

    if user_preferences: # response generation
        user_preferences = "User Preferences: " + ". ".join(user_preferences) + "\n"
    else: # summarization
        prompt_text += "\n"

    p = prompt_text + user_text + user_preferences + dialogue + final_response
    print(p)

    return p


def prompt(prompt_file_path, username, dialogue, user_preferences, final_response_bool):
    data["prompt"] = build_prompt(prompt_file_path, username, dialogue, user_preferences, final_response_bool)
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


def get_dialogue_history(user_name, entire_dialogue_bool):
    with (open(f"./data/{user_name}/event.json", "r") as file):
        dialogue_history = json.load(file)
    dialogue = ""
    if entire_dialogue_bool:
        for entry in dialogue_history[:-1]: # Go through every element except the last one
            irony_text = ""
            if entry['irony']:
                irony_text = f"Keep in mind that the user is being ironic in interaction {entry['id']}:\n"
            summary = f"Interaction {entry['id']}: {entry['summarized_tuple']}\n"
            dialogue += f"{irony_text}{summary}"
    last_dialog = dialogue_history[-1]
    irony_text = ""
    if last_dialog['irony']:
        irony_text = "Keep in mind that the user is being ironic in the last interaction:\n"
    summary = f"Last interaction: {last_dialog['summarized_tuple']}\n"
    dialogue += f"{irony_text}{summary}"

    return dialogue


def get_last_utterances(question, user_answer):
    
    return f"Question: {question}\nUser_answer: {user_answer}"


def summarization(question, user_answer):
    username = load_config()['settings']['user']
    prompt_file_path = Path(r"LLM/Prompts/summarization.txt")
    dialogue = get_last_utterances(question, user_answer)

    return prompt(prompt_file_path, username, dialogue, "", False)


def response_generation(user_preferences, final_response_bool):
    username = load_config()['settings']['user']
    if user_preferences: # memory condition
        dialogue = get_dialogue_history(username, True)
        prompt_file_path = Path(r"LLM/Prompts/with_memory_response_generation.txt")
    else: # no memory condition
        dialogue = get_dialogue_history(username, False)
        prompt_file_path = Path(r"LLM/Prompts/no_memory_response_generation.txt")
    # print(dialogue)

    return prompt(prompt_file_path, username, dialogue, user_preferences, final_response_bool)


