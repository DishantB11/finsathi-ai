"""
FinSathi AI - RAG Pipeline
Pure keyword-based retrieval — no ML model, no chromadb needed at runtime.
Zero extra RAM cost — fits comfortably in Render's 512MB free tier.
"""

from knowledge_base import FINSATHI_KNOWLEDGE_BASE


def retrieve_context(query: str, top_k: int = 3) -> str:
    """Return top-k most relevant knowledge chunks using keyword scoring."""
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored = []
    for doc in FINSATHI_KNOWLEDGE_BASE:
        content_lower = doc["content"].lower()
        topic_lower   = doc["topic"].lower()
        score = sum(1 for w in query_words if w in content_lower or w in topic_lower)
        if any(w in topic_lower for w in query_words):
            score += 3
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)

    context_parts = []
    for i, (_, doc) in enumerate(scored[:top_k]):
        context_parts.append(f"[Source {i+1} - {doc['topic']}]\n{doc['content']}")

    return "\n\n".join(context_parts)


def get_sources(query: str, top_k: int = 3) -> list:
    """Return list of source topic names for the top-k matches."""
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored = []
    for doc in FINSATHI_KNOWLEDGE_BASE:
        content_lower = doc["content"].lower()
        topic_lower   = doc["topic"].lower()
        score = sum(1 for w in query_words if w in content_lower or w in topic_lower)
        if any(w in topic_lower for w in query_words):
            score += 3
        scored.append((score, doc["topic"]))

    scored.sort(reverse=True)
    # Deduplicate while preserving order
    seen = set()
    sources = []
    for _, topic in scored[:top_k * 2]:
        if topic not in seen:
            seen.add(topic)
            sources.append(topic)
        if len(sources) == top_k:
            break
    return sources
