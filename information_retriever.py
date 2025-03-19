import torch
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel
from utils import *


def init_retrieve_model():
    tokenizer = AutoTokenizer.from_pretrained('facebook/contriever')
    model = AutoModel.from_pretrained('facebook/contriever').to("cpu")
    return model, tokenizer


def embed_text(text, model, tokenizer):
    '''
    Embed a single text
    '''
    model.eval()
    with torch.no_grad():
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding.numpy()
  
  
def embed_texts(texts, model, tokenizer):
    '''
    Embed a list of texts
    '''
    model.eval()
    embeddings = []
    with torch.no_grad():
        for text in texts:
            input = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
            outputs = model(**input)
            embeddings.append(outputs.last_hidden_state.mean(dim=1)[0])
    return np.array(embeddings)
    

def faiss_search(memory, query, k = 3):
    '''
    Query comes from the context, which might be key words extraction from the conversation
    Then we retrieve the preference from the long-term memory, and the event from the short-term memory
    Ref: https://medium.com/loopio-tech/how-to-use-faiss-to-build-your-first-similarity-search-bf0f708aa772
    '''
    # Normalize the vectors
    faiss.normalize_L2(memory)
    faiss.normalize_L2(query)
    
    # Add the memory to the index
    index = faiss.IndexFlatL2(memory.shape[1]) 
    index.add(memory)
    
    # Search the query in the index
    _, indices = index.search(query, k)
    return indices[0]


def retrieve(model, tokenizer, query_text, memory_type):
    config = load_config()
    
    query = embed_text(query_text, model, tokenizer) 
    memory_text = load_json('preference.json') if memory_type == 'preference' else load_event_json('event.json')
    memory = embed_texts(memory_text, model, tokenizer)
    
    # Search k nearest memory (kNN search)
    k = config['settings']['k']
    indices = faiss_search(memory, query, k)
    output = [memory_text[indices[i]] for i in range(k)]
    print(f"Query: {query_text}, Memory type: {memory_type}, Output: {output}")
    return output
