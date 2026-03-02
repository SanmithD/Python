import re
import datetime

def sentence_split(text):
    sentence = re.split(r'(?<=[.!?])\s+', text.strip())
    return sentence

def estimate_token(text):
    return int(len(text.split()) / 0.75) # it means 1 token is approx 0.75 words

def chunk_text(
        text,
        chunk_text_size=600,
        overlap_tokens=150,
        source="unknown"
):
    sentences = sentence_split(text)

    chunks = []
    current_chunk = []
    current_tokens = 0
    chunk_id = 0

    for sentence in sentences:
        sentence_token = estimate_token(sentence)

        if current_tokens + sentence_token > chunk_text_size:
            chunk_text_combined = " ".join(current_chunk)

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text_combined,
                "source": source,
                "estimated_token": sentence_token,
                "createdAt": datetime.utcnow()
            })

            chunk_id += 1

            # Overlapping
            overlap_text = " ".join(current_chunk)[-overlap_tokens:]
            current_chunk = [overlap_text]
            current_tokens = estimate_token(overlap_text)
        
        current_chunk.append(sentence)
        current_tokens += sentence_token

    if current_chunk:
        chunks.append({
            "chunk_id": chunk_id,
            "text": " ".join(current_chunk),
            "source": source,
            "estimated_token": current_tokens,
            "createdAt": datetime.utcnow()
        })

    return chunks
