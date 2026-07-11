# FinSathi AI - Configuration
# In production, values should come from environment variables.

import os

IBM_API_KEY = os.environ.get("IBM_API_KEY", "").strip()
IBM_PROJECT_ID = os.environ.get("IBM_PROJECT_ID", "").strip()
IBM_URL = os.environ.get("IBM_URL", "https://us-south.ml.cloud.ibm.com").strip()

# granite-4-h-small is a lightweight default for this app.
GRANITE_MODEL_ID = (
    os.environ.get("GRANITE_MODEL_ID", "ibm/granite-4-h-small").strip()
    or "ibm/granite-4-h-small"
)

# ChromaDB settings
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "finsathi_knowledge"

# Embedding model (runs locally, no API needed)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG settings
TOP_K_RESULTS = 3
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.7


def missing_ibm_settings() -> list[str]:
    missing = []
    if not IBM_API_KEY:
        missing.append("IBM_API_KEY")
    if not IBM_PROJECT_ID:
        missing.append("IBM_PROJECT_ID")
    if not IBM_URL:
        missing.append("IBM_URL")
    return missing
