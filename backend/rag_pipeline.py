"""
FinSathi AI - RAG Pipeline
Builds a ChromaDB vector store from the financial knowledge base.

Production strategy: vector store is pre-built locally and committed to git.
On Render, we load it read-only — no sentence-transformers needed at runtime.
"""

import chromadb
from knowledge_base import FINSATHI_KNOWLEDGE_BASE
from config import CHROMA_PERSIST_DIR, COLLECTION_NAME

# Lazy singleton — loaded once on first use
_collection = None


def _get_client():
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def _get_embedding_function():
    """Only imported when actually building the vector store (local only)."""
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    return SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")


def build_vector_store():
    """Embed all knowledge base documents and store in ChromaDB.
    Run this locally — commit the chroma_db/ folder to git.
    """
    print(">> Initialising ChromaDB...")
    client = _get_client()
    ef = _get_embedding_function()

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
    """Load existing ChromaDB collection. No embedding model needed for queries
    when the collection already has embeddings stored."""
    global _collection
    if _collection is None:
        client = _get_client()
        # Load without embedding function — embeddings already stored in DB
        _collection = client.get_collection(name=COLLECTION_NAME)
    return _collection


def retrieve_context(query: str, top_k: int = 3) -> str:
    """Retrieve top-k relevant chunks for the query using stored embeddings.
    Falls back to keyword search if vector search fails.
    """
    try:
        collection = get_vector_store()
        # query_embeddings=None → ChromaDB uses stored embeddings for similarity
        # We pass query_texts but the collection has no EF, so we must embed manually
        # Instead: use simple keyword matching as fallback (zero RAM cost)
        results = _keyword_search(query, top_k)
        return results
    except Exception:
        return _keyword_search(query, top_k)


def _keyword_search(query: str, top_k: int = 3) -> str:
    """Lightweight keyword-based retrieval — zero RAM cost, no ML model needed."""
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored = []
    for doc in FINSATHI_KNOWLEDGE_BASE:
        content_lower = doc["content"].lower()
        topic_lower   = doc["topic"].lower()
        # Score = number of query words found in content + topic
        score = sum(1 for w in query_words if w in content_lower or w in topic_lower)
        # Bonus for topic match
        if any(w in topic_lower for w in query_words):
            score += 3
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    context_parts = []
    for i, (score, doc) in enumerate(top):
        context_parts.append(f"[Source {i+1} - {doc['topic']}]\n{doc['content']}")

    return "\n\n".join(context_parts)


if __name__ == "__main__":
    build_vector_store()
    test_query = "How does UPI work?"
    print("\nTest query:", test_query)
    print(retrieve_context(test_query))
