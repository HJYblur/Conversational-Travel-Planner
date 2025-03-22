from utils import *
from information_retriever import *


def main():
    # Step1: System initialization
    record_init()
    GUI_init()
    
    # Step2-6 should be in a for loop
    # Step2: Recode the user speech and convert it to text (livekit)
    
    # Step3: Summarize short-term memory from the text
    
    # Step4.1: Information retrieval from long-term memory(preference)
    model, tokenizer = init_retrieve_model()
    query = 'I want to go to the beach'
    retrieved_preference = retrieve(model, tokenizer, query, 'preference')
    
    # Step4.2(optional): Information retrieval from semantic memory
    
    # Step5: Communicate with LLM to generate the response
    
    # Step6: Convert the LLM response to speech and output to users
    
    # Step7: Thank user for participating, end GUI
    
    
    
if __name__ == '__main__':
    main()