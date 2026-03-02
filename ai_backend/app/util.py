from app.retrieval import retrieve_documents, re_ranker, multi_retrieve
from app.chunking import estimate_token


def build_context(
        query,
        max_tokens=1200,
        k=10,
        threshold=0.80
):
    results = retrieve_documents(query, k=k)
    results = multi_retrieve(query)
    results = re_ranker(query, results)

    results = [r for r in results if r["score"] >=  threshold]

    results = sorted(results, key=lambda x:x["score"], reverse=True)

    context_chunk = []
    total_tokens = 0

    for r in results:
        chunk_tokens = estimate_token(r["text"])

        if total_tokens + chunk_tokens > max_tokens:
            break

        context_chunk.append(r["text"])
        total_tokens += chunk_tokens

    final_context = "\n\n".join(context_chunk)

    return {
        "context": final_context,
        "used_tokens": total_tokens,
        "num_chunks": len(context_chunk)
    }