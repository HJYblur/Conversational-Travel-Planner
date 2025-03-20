from utils import *
from information_retriever import *


def main():
    print('Hello, welcome to the travel recommendation agent!')
    user_init()
    
    # Information retrieval
    model, tokenizer = init_retrieve_model()
    query = 'I want to go to the beach'
    # TODO: test for single round here, should be replaced by a loop
    retrieved_preference = retrieve(model, tokenizer, query, 'preference')
    retrieved_event = retrieve(model, tokenizer, query, 'event')
    
    
if __name__ == '__main__':
    main()