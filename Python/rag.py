from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from SYSTEM_INSTRACTION import DOCS

embed_model = SentenceTransformer("all-MiniLM-L6-v2") # Pre trained model converts sentence to vectors ( Numbers )

vectors = embed_model.encode(DOCS) # Convert document to vector

index = faiss.IndexFlatL2(vectors.shape[1])

index.add(np.array(vectors))

def search_knowledge(query):

    q_vec = embed_model.encode([query])
    _, idx = index.search(np.array(q_vec), k=2) # returns top 2 documents nearest to results

    return [DOCS[i] for i in idx[0]] # returning 1st result
