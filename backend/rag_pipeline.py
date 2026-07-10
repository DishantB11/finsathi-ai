"""
FinSathi AI – RAG Pipeline
Builds a ChromaDB vector store from the financial knowledge base.
Compatible with chromadb >= 1.0.0
"""

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from knowledge_base import FINSATHI_KNOWLEDGE_BASE
from config import CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL


def _get_client():
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def _get_embedding_function():
    return SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)


def build_vector_store():
    """Embed all knowledge base documents and store in ChromaDB."""
    print(">> Initialising ChromaDB...")
    client = _get_client()
    ef = _get_embedding_function()

    # Delete existing collection so we can rebuild cleanly
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(">> Deleted existing collection: " + COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    ids       = [doc["id"]      for doc in FINSATHI_KNOWLEDGE_BASE]
    documents = [doc["content"] for doc in FINSATHI_KNOWLEDGE_BASE]
    metadatas = [{"topic": doc["topic"]} for doc in FINSATHI_KNOWLEDGE_BASE]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(">> Vector store built. Documents indexed: " + str(len(ids)))
    return collection


def get_vector_store():
    """Load the existing ChromaDB collection (build_vector_store must be called first)."""
    client = _get_client()
    ef = _get_embedding_function()
    return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)


def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Given a user query, return the top-k most relevant knowledge chunks
    as a single formatted string to inject into the Granite prompt.
    """
    collection = get_vector_store()
    results = collection.query(query_texts=[query], n_results=top_k)

    context_parts = []
    for i, (doc, meta) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        context_parts.append(f"[Source {i+1} - {meta['topic']}]\n{doc}")

    return "\n\n".join(context_parts)


if __name__ == "__main__":
    build_vector_store()
    test_query = "How does UPI work?"
    print(f"\nTest query: '{test_query}'")
    print(retrieve_context(test_query))
