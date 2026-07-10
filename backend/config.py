# FinSathi AI - Configuration
# In production (Docker/Code Engine), values come from environment variables.
# In local dev, values are set directly here.

import os

IBM_API_KEY    = os.environ.get("IBM_API_KEY",    "YwK84zc1QRP9C7rXc3p07l6zIeqMhIUALWbjOKCkKOkz")
IBM_PROJECT_ID = os.environ.get("IBM_PROJECT_ID", "c7932346-d14d-43fc-8274-39808c17a8bc")
IBM_URL        = os.environ.get("IBM_URL",        "https://us-south.ml.cloud.ibm.com")

# granite-4-h-small — latest IBM Granite model available in this environment
GRANITE_MODEL_ID = "ibm/granite-4-h-small"

# ChromaDB settings
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "finsathi_knowledge"

# Embedding model (runs locally, no API needed)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG settings
TOP_K_RESULTS = 3
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.7
