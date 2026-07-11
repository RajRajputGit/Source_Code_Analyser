"""
Streamlit frontend for the Source Code Analyser.

This is a thin client that just calls the FastAPI backend.
The backend is the source of truth — it owns the LLM, the retriever,
and the conversation memory.

Run
---
    streamlit run frontend/streamlit_app.py
"""

import uuid
import requests
import streamlit as st

# Default points at the local FastAPI server started via `uvicorn backend.main:app`.
DEFAULT_API_BASES = ["http://127.0.0.1:8080", "http://127.0.0.1:8000"]
API_BASE = "http://127.0.0.1:8080"  # default fallback
for base in DEFAULT_API_BASES:
    try:
        r = requests.get(f"{base}/", timeout=0.5)
        if r.status_code == 200:
            API_BASE = base
            break
    except Exception:
        continue

st.set_page_config(
    page_title="Source Code Analyser",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Source Code Analyser")
st.caption(
    "Chat with the codebase. Powered by a FastAPI backend + RAG + rolling summary memory."
)

# ---------- Session id ----------
# A single user keeps the same id across reloads so the conversation
# summary persists. We store it in st.session_state the first time the
# app loads.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []  # list[dict(role, content)]

# ---------- Sidebar ----------
with st.sidebar:
    st.subheader("Session")
    st.code(st.session_state.session_id, language=None)

    api_base = st.text_input("API base URL", value=API_BASE)
    if api_base != API_BASE:
        API_BASE = api_base

    # Let user specify which Git Repository to analyze
    DEFAULT_REPO = "https://github.com/RajRajputGit/Source_Code_Analyser.git"
    repo_url = st.text_input("Git Repository URL", value=DEFAULT_REPO)

    if st.button("New conversation"):
        # Ask the backend to delete local vector data & cloned repo
        # so the next conversation starts completely fresh.
        try:
            requests.post(
                f"{API_BASE}/new-conversation",
                json={"repo_url": repo_url},
                timeout=10,
            )
        except Exception:
            pass  # best-effort; the conversation still resets locally
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("**Backend status**")
    try:
        h = requests.get(f"{API_BASE}/health", timeout=3).json()
        st.success(f"OK — ready={h.get('ready')}")
    except Exception as e:
        st.error(f"Cannot reach backend: {e}")

    st.divider()
    st.markdown("**Current summary**")
    try:
        s = requests.get(
            f"{API_BASE}/summary/{st.session_state.session_id}", timeout=3
        ).json()
        summary = s.get("summary", "(empty)")
    except Exception:
        summary = "(backend offline)"
    st.text_area("memory", value=summary, height=200, disabled=True)

# ---------- Render previous turns ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Chat input ----------
prompt = st.chat_input("Ask something about the repo…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                resp = requests.post(
                    f"{API_BASE}/chat",
                    json={
                        "session_id": st.session_state.session_id,
                        "question": prompt,
                        "repo_url": repo_url,
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data["answer"]
                summary = data.get("summary", "")
            except requests.HTTPError as e:
                answer = f"Backend error: {e.response.status_code} — {e.response.text}"
                summary = ""
            except Exception as e:
                answer = f"Request failed: {e}"
                summary = ""

            st.markdown(answer)

            if summary:
                with st.expander("🧾 Updated conversation summary"):
                    st.write(summary)

    st.session_state.messages.append({"role": "assistant", "content": answer})
