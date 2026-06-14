import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

os.environ["GROQ_API_KEY"] = api_key


def get_llm():
    llm = ChatGroq(api_key=api_key, model="llama3-8b-8192")
    return llm
