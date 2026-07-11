# FinSathi AI - Configuration
# In production, values should come from environment variables.

import hashlib
import os

_API_KEY_SOURCE = "IBM_API_KEY"
_RAW_IBM_API_KEY = os.environ.get("FINSATHI_IBM_API_KEY", "")
if _RAW_IBM_API_KEY:
    _API_KEY_SOURCE = "FINSATHI_IBM_API_KEY"
else:
    _RAW_IBM_API_KEY = os.environ.get("IBM_API_KEY", "")
IBM_API_KEY = _RAW_IBM_API_KEY.strip()
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


def ibm_api_key_diagnostics() -> dict:
    stripped = IBM_API_KEY
    return {
        "source": _API_KEY_SOURCE,
        "present": bool(_RAW_IBM_API_KEY),
        "raw_length": len(_RAW_IBM_API_KEY),
        "stripped_length": len(stripped),
        "changed_by_strip": _RAW_IBM_API_KEY != stripped,
        "starts_with_quote": stripped.startswith(("'", '"')),
        "ends_with_quote": stripped.endswith(("'", '"')),
        "contains_space": " " in stripped,
        "contains_tab": "\t" in _RAW_IBM_API_KEY,
        "contains_newline": "\n" in _RAW_IBM_API_KEY or "\r" in _RAW_IBM_API_KEY,
        "sha256_prefix": (
            hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:12]
            if stripped
            else ""
        ),
    }
