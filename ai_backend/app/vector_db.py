import faiss
import numpy as np
from app.ollama_client import generate_embedding
from app.util import chuck_text

dimension = 768  # nomic-embed-text dimension

index = faiss.IndexFlatIP(dimension)

documents = []
metadata_store = []


def add_document(texts, metadata=None):
    global documents, metadata_store

    chunks = chuck_text(texts)

    embeddings = []

    for chunk in chunks:
        emb = np.array(generate_embedding(chunk), dtype="float32")
        faiss.normalize_L2(emb.reshape(1, -1))

        embeddings.append(emb)
        documents.append(chunk)
        metadata_store.append(metadata)
    
    if len(embeddings) == 0:
        return
    
    embeddings = np.vstack(embeddings)
    index.add(embeddings)


def search_document(query, k=3, threshold=0.7):

    if index.ntotal == 0:
        return []

    query_embedding = np.array(
        generate_embedding(query),
        dtype="float32"
    ).reshape(1, -1)

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, k)

    results = []

    for s, i in zip(scores[0], indices[0]):
        if i < len(documents) and s > threshold:
            results.append({
                "text": documents[i],
                "score": float(s),
                "metadata": metadata_store[i]
            })

    return results
