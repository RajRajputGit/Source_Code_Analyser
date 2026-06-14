"""
summary.py
----------
Maintains a rolling summary of long conversations AND
builds a RAG answer chain that uses that summary as context.

Workflow
--------
User asks a question
      ↓
1. Pull the current summary for this session
      ↓
2. Retrieve relevant code chunks
      ↓
3. Stuff everything (summary + code + question) into the LLM prompt
      ↓
4. Get the answer
      ↓
5. Append the new turn to history
      ↓
6. Ask the LLM to merge old summary + new turn into an updated summary
      ↓
7. Save the updated summary back into the session store
"""

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ConversationSummaryManager:
    """
    Two jobs:
        1. Build a RAG ("stuff documents") chain that includes the
           rolling summary as part of the prompt context.
        2. Update that rolling summary after every turn.
    """

    def __init__(self, llm):
        """
        Store the LLM once and pre-build both prompt templates.
        """
        self.llm = llm

        # ------------------------------------------------------------------
        # Prompt #1: used to UPDATE the rolling summary after each turn.
        # ------------------------------------------------------------------
        self.summary_update_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a conversation summarizer.

Update the existing summary using the latest conversation.

Rules:
- Keep important facts.
- Remove unnecessary details.
- Keep user preferences.
- Keep unresolved questions.
- Maximum 250 words.
""",
                ),
                (
                    "human",
                    """
Previous Summary:

{summary}

Latest Conversation:

{conversation}

Return only the updated summary.
""",
                ),
            ]
        )

        # Chain that takes {"summary": str, "conversation": str}
        # and returns a Message object -> we read .content below.
        self.summary_update_chain = self.summary_update_prompt | self.llm

        # ------------------------------------------------------------------
        # Prompt #2: used to ANSWER the user's question using BOTH
        # the retrieved code chunks AND the rolling conversation summary.
        # ------------------------------------------------------------------
        self.rag_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful AI assistant that analyses source code.

You have three sources of information:

1. Conversation Summary (what we discussed before; may be empty on the first turn):
{summary}

2. Retrieved code chunks from the repository (treat these as ground truth).

3. The user's current question.

If the summary is empty, ignore it and rely only on the retrieved code.
Answer clearly and concisely.""",
                ),
                (
                    "human",
                    """Retrieved code context:
{context}

Current question: {input}""",
                ),
            ]
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_stuff_documents_chain(self):
        """
        Build a "stuff documents" chain.

        "Stuff documents" simply means: take all retrieved documents,
        concatenate their text into one big string, and stuff that
        string into the prompt's {context} placeholder.

        The returned chain expects a dict with these keys:
            - "context"  : list[Document]   (output of retriever.invoke)
            - "input"    : str              (the user's question)
            - "summary"  : str              (the current rolling summary)

        It returns a plain string answer.
        """
        llm = self.llm
        prompt = self.rag_prompt

        def format_docs(docs):
            """Join all retrieved documents into one big text block."""
            return "\n\n".join(doc.page_content for doc in docs)

        # A dict of lambdas piped into a prompt is automatically turned
        # into a RunnableParallel by LangChain, so this is the standard
        # "prepare the variables" pattern.
        chain = (
            {
                "context": lambda x: format_docs(x["context"]),
                "input": lambda x: x["input"],
                "summary": lambda x: x.get("summary", ""),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain

    def update_summary(self, previous_summary: str, messages: list) -> str:
        """
        Update the rolling summary.

        Parameters
        ----------
        previous_summary : str
            The summary we had before this turn.

        messages : list
            Recent HumanMessage / AIMessage objects (the newest turns).

        Returns
        -------
        str
            The new, merged summary.
        """
        conversation = self._format_messages(messages)

        response = self.summary_update_chain.invoke(
            {
                "summary": (
                    previous_summary if previous_summary else "No prior summary."
                ),
                "conversation": conversation,
            }
        )
        return response.content

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _format_messages(self, messages):
        """
        Convert LangChain message objects into plain text.

        Example output:

            Human: Hello
            AI: Hi there
            Human: Explain RAG
        """
        formatted = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted.append(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                formatted.append(f"AI: {msg.content}")
        return "\n".join(formatted)
