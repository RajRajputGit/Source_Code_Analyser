# Main entry point for the lightweight Python application.
#
# Flow per turn:
#   1. Look up the rolling summary for this session_id.
#   2. Retrieve relevant code chunks for the user's question.
#   3. Pass summary + code + question into the "stuff documents" chain.
#   4. Save the new turn into history.
#   5. Recompute and store an updated summary.

import os
from dotenv import load_dotenv

from config import LLMConfig, retriever_config
from src.vectordata import create_vectordata
from src.state.summary import ConversationSummaryManager
from src.state.session_store import sessions
from src.state.history import (
    add_user_message,
    add_ai_message,
    get_recent_messages,
)

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

os.environ["GROQ_API_KEY"] = api_key


def run_turn(session_id, question, retriever, stuff_chain, summary_manager):
    """
    Pure per-turn logic. No prints. No HTTP.

    Used by BOTH the CLI demo below AND the FastAPI backend in backend/main.py.

    Returns
    -------
    dict with keys: "answer", "summary"
    """
    # 1) Read the summary we already have for this session.
    current_summary = sessions.get_summary(session_id)

    # 2) Pull relevant code chunks for the question.
    docs = retriever.invoke(question)

    # 3) Run the RAG chain. The prompt has three placeholders:
    #    {context} = joined retrieved code
    #    {input}   = the user's question
    #    {summary} = the rolling conversation summary
    answer = stuff_chain.invoke(
        {
            "context": docs,
            "input": question,
            "summary": current_summary,  # may be "" on the first turn
        }
    )

    # 4) Record this turn in the full message history.
    add_user_message(session_id, question)
    add_ai_message(session_id, answer)

    # 5) Recompute the rolling summary and store it for next time.
    recent = get_recent_messages(session_id, limit=6)
    new_summary = summary_manager.update_summary(current_summary, recent)
    sessions.update_summary(session_id, new_summary)

    return {"answer": answer, "summary": new_summary}


def ask(session_id, question, retriever, stuff_chain, summary_manager):
    """
    CLI wrapper around run_turn() that prints to stdout.
    Kept so `python app.py` still works as a smoke test.
    """
    print(f"\n[session {session_id}] you > {question}")
    result = run_turn(session_id, question, retriever, stuff_chain, summary_manager)
    print(f"[session {session_id}] ai  > {result['answer']}")
    return result["answer"]


def main():
    print("Initializing application...")

    # LLM
    # llama3-8b-8192 was decommissioned by Groq.
    # llama-3.1-8b-instant is the current supported 8B model.
    llm = LLMConfig(api_key, model="llama-3.1-8b-instant").get_llm()

    # Vector DB over the GitHub repo
    # NOTE: pass the .git clone URL, NOT the /tree/branch web URL.
    _, vector_db = create_vectordata(
        url="https://github.com/RajRajputGit/Source_Code_Analyser.git",
        path="./repo_sample",  # local folder, not the parent project dir
    )

    # Retriever (k=8, MMR)
    retriever = retriever_config(
        embedding=None,  # not used inside get_retriever(); placeholder for symmetry
        vector_db=vector_db,
    ).get_retriever()

    # Summary manager + RAG stuff chain
    summary_manager = ConversationSummaryManager(llm)
    stuff_chain = summary_manager.get_stuff_documents_chain()

    # ----------------- Demo conversation -----------------
    # Use ONE session_id so the summary actually evolves across turns.
    session_id = "demo-session-1"

    # Try a couple of repo-scoped questions so the summary has something
    # to summarize on the second turn.
    ask(session_id, "Explain ETL", retriever, stuff_chain, summary_manager)
    ask(
        session_id,
        "How is it used in this repo?",
        retriever,
        stuff_chain,
        summary_manager,
    )

    print("\n--- Final summary for this session ---")
    print(sessions.get_summary(session_id))


if __name__ == "__main__":
    main()
