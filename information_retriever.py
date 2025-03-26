import torch
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel
from utils import load_json, get_json_size
from configure_loader import load_config


def init_retrieve_model():
    global tokenizer, retrieve_model
    if "tokenizer" not in globals() or "retrieve_model" not in globals():
        tokenizer = AutoTokenizer.from_pretrained('facebook/contriever')
        retrieve_model = AutoModel.from_pretrained('facebook/contriever').to("cpu")
    return retrieve_model, tokenizer


def embed_text(text, retrieve_model, tokenizer):
    '''
    Embed a single text
    '''
    retrieve_model.eval()
    with torch.no_grad():
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        outputs = retrieve_model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding.numpy()
  
  
def embed_texts(texts, retrieve_model, tokenizer):
    '''
    Embed a list of texts
    '''
    retrieve_model.eval()
    embeddings = []
    with torch.no_grad():
        for text in texts:
            input = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
            outputs = retrieve_model(**input)
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


def retrieve(query_text, memory_type):
    config = load_config()
    init_retrieve_model()
    
    query = embed_text(query_text, retrieve_model, tokenizer) 
    memory_text = load_json(memory_type) # memory_type == 'preference' or 'event'
    memory = embed_texts(memory_text, retrieve_model, tokenizer)
    
    # Search k nearest memory (kNN search)
    k = min(config['settings']['k'], get_json_size(memory_type))
    indices = faiss_search(memory, query, k)
    output = [memory_text[indices[i]] for i in range(k)]
    print(f"Query: {query_text}, Output: {output}")
    return output
