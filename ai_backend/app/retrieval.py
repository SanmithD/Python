from app.ollama_client import generate_embedding
from app.vector_db import collection
from app.chunking import chunk_text
from app.query_expansion import expand_query

EMBED_MODEL = "tinyllama"

def add_document(
        texts,
        source="unknown", 
        metadata=None
):
    chunks = chunk_text(texts)

    docs_to_insert = []

    for chunk in chunks:
        embeddings = generate_embedding(chunk["text"])
        docs_to_insert.append({
            "text": chunk["text"],
            "embedding": embeddings,
            "embedding_model": EMBED_MODEL,
            "embedding_dim": len(embeddings),
            "chunk_id": chunk["chunk_id"],
            "source": chunk["source"],
            "estimated_token": chunk["estimated_token"],
            "metadata": metadata,
            "createdAt": chunk["createdAt"]
        })
    
    if docs_to_insert:
        collection.insert_many(docs_to_insert)


def retrieve_documents(query, k=3):

    query_embedding = generate_embedding(query)

    pipeline = [
        {
            '$vectorSearch' : {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": k
            }
        },
        {
            '$project':{
                "text": 1,
                "metadata": 1,
                "source": 1,
                "chunk_id": 1,
                "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]

    return list(collection.aggregate(pipeline))

def filter_by_threshold(results, threshold=0.85):
    return [r for r in results if r["score"] >= threshold]

def multi_retrieve(query, k=5):

    queries = expand_query(query)

    all_results = []

    for q in queries:
        results = retrieve_documents(q, k=k)
        all_results.extend(results)

    # Remove duplicates by chunk_id
    seen = set()
    unique_results = []

    for r in all_results:

        cid = r.get("chunk_id")
        if cid not in seen:
            seen.add(cid)
            unique_results.append(r)
    
    return unique_results

def re_ranker(query, results):

    query_words = set(query.lower().split())

    for r in results:

        text_word = set(r["text"].lower().split())
        overlap = len(query_words.intersection(text_word))
        r["rerank_score"] = r["score"] + (0.01 * overlap)
    
    return sorted(results, key=lambda x:x["rerank_score"], reverse=True)