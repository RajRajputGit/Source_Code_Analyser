"""
FastAPI backend for the Source Code Analyser.

Layout
------
  /        GET  -> small HTML hint page (so you can open it in a browser)
  /health  GET  -> liveness check
  /chat    POST -> { "session_id": "...", "question": "..." }
                 -> { "answer": "...", "summary": "..." }

The heavy stuff (clone repo, build vector DB, create LLM, create retriever,
create stuff-documents chain) is done ONCE on first request and then cached
in `app.state`. After that every /chat call is fast.

Run it
------
    uvicorn backend.main:app --reload --port 8000 /
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Make the project root importable so we can reuse `run_turn` from app.py
# regardless of where this file is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Reuse the per-turn logic from app.py. We deliberately do NOT re-implement
# it here so the CLI demo (`python app.py`) and the API stay in sync.
from app import run_turn  # noqa: E402

from config import LLMConfig, retriever_config  # noqa: E402
from src.state.summary import ConversationSummaryManager  # noqa: E402
from src.state.session_store import sessions  # noqa: E402
from src.vectordata import create_vectordata  # noqa: E402

load_dotenv()

# ---------- Request / response models ----------


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Stable per-user id")
    question: str = Field(..., min_length=1)
    repo_url: str = Field(None, description="The Git repository URL to analyze")


class ChatResponse(BaseModel):
    answer: str
    summary: str


# ---------- One-time setup ----------

DEFAULT_REPO_URL = "https://github.com/RajRajputGit/Source_Code_Analyser.git"


def _build_components(repo_url: str):
    """
    Build the LLM, vector DB, retriever, summary manager, and stuff chain.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")
    os.environ["GROQ_API_KEY"] = api_key

    llm = LLMConfig(api_key, model="llama-3.1-8b-instant").get_llm()

    # Determine unique local paths based on the repo name to avoid conflicts.
    import urllib.parse
    parsed = urllib.parse.urlparse(repo_url)
    repo_name = parsed.path.strip("/").replace("/", "_").replace(".git", "")
    if not repo_name:
        repo_name = "default_repo"

    path = f"./repo_sample/{repo_name}"
    persist_directory = f"./vectordata/{repo_name}"

    _, vector_db = create_vectordata(
        url=repo_url,
        path=path,
        persist_directory=persist_directory,
    )

    retriever = retriever_config(
        embedding=None,
        vector_db=vector_db,
    ).get_retriever()

    summary_manager = ConversationSummaryManager(llm)
    stuff_chain = summary_manager.get_stuff_documents_chain()

    return {
        "llm": llm,
        "retriever": retriever,
        "stuff_chain": stuff_chain,
        "summary_manager": summary_manager,
    }


# ---------- FastAPI app with a "lifespan" so we can init eagerly if we want ----------


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lazy init: do NOT build anything here. First /chat will build it.
    app.state.components = {}
    yield
    app.state.components = {}


app = FastAPI(
    title="Source Code Analyser API",
    version="1.0.0",
    lifespan=lifespan,
)

# Streamlit runs on :8501 by default. CORS is permissive on purpose for
# local development; tighten it in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_components(repo_url: str):
    """Lazy initializer for the heavy RAG components for a specific repo."""
    if repo_url not in app.state.components:
        app.state.components[repo_url] = _build_components(repo_url)
    return app.state.components[repo_url]


# ---------- Endpoints ----------


@app.get("/")
def root():
    return {
        "service": "Source Code Analyser",
        "docs": "/docs",
        "health": "/health",
        "chat": "POST /chat  body={session_id, question, repo_url}",
    }


@app.get("/health")
def health():
    ready = len(app.state.components) > 0
    return {"status": "ok", "ready": ready}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    repo_url = req.repo_url or DEFAULT_REPO_URL
    try:
        comps = _get_components(repo_url)
    except Exception as e:
        # First-time init failure (e.g. no internet, no API key).
        raise HTTPException(status_code=503, detail=f"Init failed: {e}")

    try:
        result = run_turn(
            session_id=req.session_id,
            question=req.question,
            retriever=comps["retriever"],
            stuff_chain=comps["stuff_chain"],
            summary_manager=comps["summary_manager"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

    return ChatResponse(answer=result["answer"], summary=result["summary"])


# Convenience: let the frontend pull the current summary without chatting.
@app.get("/summary/{session_id}")
def get_summary(session_id: str):
    return {"session_id": session_id, "summary": sessions.get_summary(session_id)}
