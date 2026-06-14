import os
from langchain_groq import ChatGroq


class LLMConfig:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def get_llm(self):
        llm = ChatGroq(api_key=self.api_key, model=self.model)
        return llm


class retriever_config:
    def __init__(self, embedding, vector_db):
        self.embedding = embedding
        self.vector_db = vector_db

    def get_retriever(self):
        retriever = self.vector_db.as_retriever(
            search_kwargs={"k": 8}, search_type="mmr"
        )
        return retriever
