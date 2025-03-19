import tkinter as tk
from tkinter import scrolledtext

class ConversationalAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversational Travel Planner")

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=15)
        self.chat_area.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.user_input = tk.Entry(root, width=40)
        self.user_input.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

    def send_message(self):
        user_message = self.user_input.get()
        if user_message.strip():
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, "User: " + user_message + "\n")
            self.chat_area.config(state='disabled')
            self.user_input.delete(0, tk.END)
            self.respond(user_message)
        return user_message


    def respond(self, user_message):
        if user_message:
            agent_response = user_message
        else:
            agent_response = "Agent: I am here to help you."
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, agent_response + "\n")
        self.chat_area.config(state='disabled')