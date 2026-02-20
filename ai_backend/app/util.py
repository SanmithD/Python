import re

def sentence_split(text):
    sentence = re.split(r'(?<=[.!?])\s+', text.strip())
    return sentence

def chuck_text(text, max_sentence=5, overlap=2):
    sentence = sentence_split(text)

    chunks = []
    start = 0

    while start < len(sentence):
        end = start + max_sentence
        chunk = " ".join(sentence[start:end])
        chunks.append(chunk)

        start += max_sentence - overlap

    return chunks

