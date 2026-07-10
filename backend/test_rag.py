"""
FinSathi AI – RAG Pipeline Test
Tests the ChromaDB vector store build and retrieval.

Usage:
    cd C:\\Users\\Dishu\\Downloads\\bob_html\\FinSathi-AI\\backend
    python test_rag.py
"""

from rag_pipeline import build_vector_store, retrieve_context

print("=" * 55)
print("  FinSathi AI - RAG Pipeline Test")
print("=" * 55)

# Step 1: Build vector store
print("\n[1/2] Building vector store from knowledge base...")
try:
    build_vector_store()
    print("      OK - Vector store built successfully!")
except Exception as e:
    print("      FAILED: " + str(e))
    print("  Fix: Run 'pip install -r requirements.txt' first")
    exit(1)

# Step 2: Test retrieval
print("\n[2/2] Testing retrieval for sample queries...\n")

test_queries = [
    "What is UPI?",
    "How to protect from online fraud?",
    "What is Jan Dhan Yojana?",
    "How to calculate EMI?",
    "What is CIBIL score?",
]

for query in test_queries:
    context = retrieve_context(query, top_k=1)
    first_line = context.split("\n")[0] if context else "(empty)"
    print("  Query : " + query)
    print("  Found : " + first_line)
    print()

print("-" * 55)
print("RAG pipeline working! Run: uvicorn main:app --reload --port 8000")
print()
