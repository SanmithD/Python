from app.ollama_client import generate_response

def expand_query(query: str):

    prompt = f"""
Generate 3 alternative search queries for following question.
Keep them short and technical.

Question:
{query}

Alternative Queries:
1.
2.
3.

"""
    response = generate_response(prompt)

    lines = response.split("\n")
    expanded = [l.strip("123. ").strip() for l in lines if l.strip()]

    return list(set([query] + expanded))
