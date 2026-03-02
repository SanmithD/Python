import requests

# ----------- TEXT GENERATION -----------
GEN_URL = "http://localhost:11434/api/generate"
GEN_MODEL = "tinyllama"

def generate_response(prompt: str):
    try:
        response = requests.post(
            GEN_URL,
            json={
                "model": GEN_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        if response.status_code != 200:
            print("Status ", response.status_code)
            print("Body ", response.text)
            response.raise_for_status()

        # response.raise_for_status()
        return response.json().get("response", "")

    except Exception as e:
        print(f"Ollama generation error: {e}")
        raise


# ----------- EMBEDDINGS -----------
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def generate_embedding(prompt: str):
    try:
        response = requests.post(
            EMBED_URL,
            json={
                "model": EMBED_MODEL,
                "prompt": prompt
            },
            timeout=120
        )

        response.raise_for_status()
        return response.json()["embedding"]

    except Exception as e:
        print(f"Ollama embedding error: {e}")
        raise
