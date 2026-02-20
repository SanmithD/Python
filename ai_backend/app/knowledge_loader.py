from app.vector_db import add_document

def load_knowledge():

    text1 = """
    FastAPI is a modern Python web framework used for building APIs.
    It supports asynchronous programming.
    It is built on Starlette and Pydantic.
    """

    text2 = """
    Vector databases store embeddings for semantic similarity search.
    They are used in retrieval augmented generation systems.
    """

    add_document(text1, metadata={"source": "fastapi_docs"})
    add_document(text2, metadata={"source": "rag_docs"})
