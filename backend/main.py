"""
FinSathi AI - FastAPI Backend
Connects IBM Granite (via watsonx.ai) with the RAG pipeline.
"""

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from rag_pipeline import retrieve_context, get_sources
from config import (
    IBM_API_KEY,
    IBM_PROJECT_ID,
    IBM_URL,
    GRANITE_MODEL_ID,
    MAX_NEW_TOKENS,
    TEMPERATURE,
)

# -- Global state --------------------------------------------------------------
model = None
jobs: dict = {}
executor = ThreadPoolExecutor(max_workers=4)


# -- Lifespan ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    print("[FinSathi] Starting up...")

    print("[FinSathi] Knowledge base loaded (keyword search, no ML model).")

    print("[FinSathi] Connecting to IBM Granite...")
    print("[FinSathi] IBM_API_KEY set: " + ("YES" if IBM_API_KEY and IBM_API_KEY != "your_ibm_api_key_here" else "NO"))
    print("[FinSathi] IBM_PROJECT_ID: " + IBM_PROJECT_ID[:8] + "...")
    print("[FinSathi] IBM_URL: " + IBM_URL)
    try:
        credentials = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
        print("[FinSathi] Credentials object created OK")
        client = APIClient(credentials=credentials, project_id=IBM_PROJECT_ID)
        print("[FinSathi] APIClient created OK")
        model = ModelInference(
            model_id=GRANITE_MODEL_ID,
            api_client=client,
            params={
                GenParams.MAX_NEW_TOKENS: MAX_NEW_TOKENS,
                GenParams.TEMPERATURE: TEMPERATURE,
                GenParams.STOP_SEQUENCES: ["Human:", "User:"],
            },
        )
        print("[FinSathi] Ready! Model loaded: " + GRANITE_MODEL_ID)
    except Exception as e:
        import traceback
        print("[FinSathi] ERROR initializing IBM Granite:")
        print(traceback.format_exc())
    yield
    executor.shutdown(wait=False)
    print("[FinSathi] Shutting down.")


# -- App -----------------------------------------------------------------------
app = FastAPI(
    title="FinSathi AI",
    description="AI Agent for Digital Financial Literacy powered by IBM Granite",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ngrok sends a browser-warning page unless we include this header in responses
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class NgrokMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

app.add_middleware(NgrokMiddleware)


# -- Schemas -------------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    language: str = "english"

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]

class JobResponse(BaseModel):
    job_id: str

class JobStatus(BaseModel):
    status: str          # "pending" | "done" | "error"
    answer: str = ""
    sources: list[str] = []
    error: str = ""


# -- Prompt builder ------------------------------------------------------------
SYSTEM_PROMPT = """You are FinSathi AI, a friendly and knowledgeable financial literacy assistant for Indian users.
You help people understand UPI, digital payments, budgeting, loans, interest rates, government schemes, and online fraud prevention.
Always answer in simple, easy-to-understand language.
Use Indian currency (Rupees/INR) and Indian context in your examples.
If the user asks in Hindi, respond in Hindi using Devanagari script.
Never give specific investment advice - always recommend consulting a certified financial advisor for personal decisions.
Use the provided context as your primary source. If the context covers the question, use it.
If the context does not fully cover the question, use your own knowledge to give a helpful, accurate answer about Indian finance.
Never make up specific numbers, interest rates, or government scheme details that you are not sure about.
"""

def build_prompt(question: str, context: str, language: str) -> str:
    lang_instruction = (
        "Please respond in Hindi (Devanagari script)."
        if language.lower() == "hindi"
        else "Please respond in clear English."
    )
    return f"""{SYSTEM_PROMPT}

{lang_instruction}

### Reference Information:
{context}

### User Question:
{question}

### FinSathi AI Answer:"""


# -- Core Granite call (blocking, runs in thread pool) ------------------------
def _call_granite(question: str, language: str) -> dict:
    context = retrieve_context(question, top_k=3)
    prompt = build_prompt(question, context, language)
    result = model.generate_text(prompt=prompt)
    answer = result.strip() if isinstance(result, str) else str(result)
    sources = get_sources(question, top_k=3)
    return {"answer": answer, "sources": sources}


def _run_job(job_id: str, question: str, language: str):
    """Submitted to thread pool executor."""
    try:
        data = _call_granite(question, language)
        jobs[job_id] = {"status": "done", "answer": data["answer"], "sources": data["sources"], "error": ""}
    except Exception as e:
        jobs[job_id] = {"status": "error", "answer": "", "sources": [], "error": str(e)}


# -- Routes --------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "name": "FinSathi AI",
        "status": "running",
        "description": "AI Agent for Digital Financial Literacy",
        "powered_by": "IBM Granite via watsonx.ai",
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": GRANITE_MODEL_ID,
        "model_loaded": model is not None,
        "api_key_set": bool(IBM_API_KEY and len(IBM_API_KEY) > 20),
        "project_id": IBM_PROJECT_ID[:8] + "..." if IBM_PROJECT_ID else "NOT SET",
        "url": IBM_URL,
    }


@app.post("/chat/async", response_model=JobResponse)
def chat_async(request: ChatRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not initialized yet.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "answer": "", "sources": [], "error": ""}
    executor.submit(_run_job, job_id, request.question, request.language)
    return JobResponse(job_id=job_id)


@app.get("/chat/result/{job_id}", response_model=JobStatus)
def chat_result(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JobStatus(**job)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not initialized yet.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        data = _call_granite(request.question, request.language)
        return ChatResponse(answer=data["answer"], sources=data["sources"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IBM Granite error: {str(e)}")


@app.post("/rebuild-knowledge-base")
def rebuild_kb():
    try:
        build_vector_store()
        return {"status": "success", "message": "Knowledge base rebuilt successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -- Serve React build (must be LAST — catches all remaining routes) -----------
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=os.path.join(STATIC_DIR, "static")), name="assets")

    @app.get("/{full_path:path}")
    def serve_react(full_path: str):
        """Serve React app for all non-API routes (client-side routing support)."""
        index = os.path.join(STATIC_DIR, "index.html")
        return FileResponse(index)
