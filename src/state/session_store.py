"""
session_store.py
----------------
Stores the rolling conversation summary, ONE PER SESSION.

In production this could be: Redis, MongoDB, Postgres, SQLite, etc.
For learning, we keep it in memory (lost when the program exits).
"""


class ConversationSummaryHistory:
    """
    Beginner-friendly summary store.

    Think of it as a small notebook:
        session_id   ->   "current summary string"

    A "session" is one continuous conversation (like a chat thread).
    Each session has its own rolling summary.
    """

    def __init__(self):
        # Private dict: { session_id (str) : summary (str) }
        self._store = {}

    def get_summary(self, session_id: str) -> str:
        """
        Return the current summary for `session_id`.
        Returns an empty string if the session has no summary yet.
        """
        return self._store.get(session_id, "")

    def update_summary(self, session_id: str, new_summary: str) -> None:
        """
        Overwrite the summary for `session_id` with `new_summary`.
        """
        self._store[session_id] = new_summary


# One shared instance that the whole app uses.
# Anywhere you `from src.state.session_store import sessions` you get
# the same object, so summaries stay in sync.
sessions = ConversationSummaryHistory()
