"""
Maintains full conversation history.
"""

from langchain_core.messages import HumanMessage, AIMessage

history_store = {}


def add_user_message(session_id, message):

    history_store.setdefault(session_id, [])

    history_store[session_id].append(HumanMessage(content=message))


def add_ai_message(session_id, message):

    history_store.setdefault(session_id, [])

    history_store[session_id].append(AIMessage(content=message))


def get_recent_messages(session_id, limit=6):
    """
    Return only recent conversation.

    We don't need the entire history because
    summary already contains old information.
    """

    return history_store.get(session_id, [])[-limit:]
