from utils import *
from information_retriever import *


def main():
    print('Hello, welcome to the travel recommendation agent!')
    user_init()
    
    # Set information retrieval
    model, tokenizer = init_retrieve_model()
    # TODO: test for single round here, should be replaced by a loop
    retrieved_preference = retrieve(model, tokenizer, 'I want to go to the beach', 'preference')
    retrieved_event = retrieve(model, tokenizer, 'I want to go to the beach', 'event')
    
    
if __name__ == '__main__':
    main()