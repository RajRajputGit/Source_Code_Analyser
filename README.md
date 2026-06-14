# 🔍 Source Code Analyser

<img width="1680" height="928" alt="Screenshot 2026-06-14 at 1 42 50 PM" src="https://github.com/user-attachments/assets/9568e4dc-d4ca-4456-95a6-f54aabf9b9df" />


> **Chat with any GitHub repository using AI.**  
> Source Code Analyser indexes a codebase into a vector database and lets you ask natural language questions through an interactive chat interface powered by **RAG (Retrieval-Augmented Generation)** and **conversation memory**.

---

## 🚀 Features

- 📂 **Analyze any GitHub repository** by simply providing its repository URL.
- 💬 **Interactive AI chat interface** built with Streamlit.
- 🧠 **Conversation Memory** with rolling summaries for long-running chats.
- 🔎 **Retrieval-Augmented Generation (RAG)** for context-aware answers.
- 📑 **Semantic code search** using vector embeddings.
- ⚡ **FastAPI backend** exposing clean REST APIs.
- 🔄 **Session-based conversations** so each chat maintains its own history.
- 📦 **Modular architecture** separating frontend, backend, retrieval, memory, and configuration.
- 📝 **Automatic conversation summarization** to reduce token usage while preserving context.
- 🤖 **LLM-powered explanations** for repositories, functions, classes, and files.

---

# 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **Backend API** | FastAPI |
| **Programming Language** | Python 3 |
| **LLM Framework** | LangChain |
| **LLM Provider** | Groq API (Llama Models) |
| **Embeddings** | LangChain Embeddings |
| **Vector Database** | ChromaDB |
| **Conversation Memory** | Custom Rolling Summary Manager |
| **Configuration** | python-dotenv (.env) |
| **HTTP Communication** | Requests |
| **Development** | VS Code |

---

# 📦 Getting Started

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/source-code-analyser.git

cd source-code-analyser
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv

source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
uv sync
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_api_key_here
```

---

## 5️⃣ Run the Backend

```bash
uvicorn backend.main:app --reload
```

By default the API runs on

```
http://127.0.0.1:8000
```

---

## 6️⃣ Run the Frontend

```bash
streamlit run frontend/streamlit_app.py
```

The Streamlit application will open automatically in your browser.

---

# 🎮 Interactive Usage Guide

Using the application is simple:

### Step 1

Launch both the **FastAPI backend** and the **Streamlit frontend**.

---

### Step 2

Paste a GitHub repository URL into the input box.

Example:

```
https://github.com/owner/repository
```

---

### Step 3

The application automatically:

- Downloads the repository
- Splits source code into chunks
- Generates embeddings
- Stores them inside the vector database

---

### Step 4

Start asking questions naturally.

Example questions:

- Explain the project architecture.
- What does this class do?
- Summarize this repository.
- Where is authentication implemented?
- Explain the API workflow.
- Which file contains database logic?

---

### Step 5

Continue chatting.

The application automatically:

- Maintains chat history
- Updates conversation summaries
- Retrieves relevant code snippets
- Generates context-aware responses

No manual memory management is required.

---

# 🧠 How It Works

```
GitHub Repository
        │
        ▼
Load Source Code
        │
        ▼
Split into Chunks
        │
        ▼
Generate Embeddings
        │
        ▼
Store in Chroma Vector DB
        │
        ▼
──────── User Question ────────
        │
        ▼
Retrieve Relevant Code
        │
        ▼
Conversation Summary
        │
        ▼
LLM Prompt
        │
        ▼
AI Response
        │
        ▼
Update Summary
```

---

# 📂 Project Structure

```text
Source_Code_Analyser/
│
├── backend/
│   ├── __init__.py
│   └── main.py                # FastAPI application
│
├── frontend/
│   └── streamlit_app.py       # Streamlit client
│
├── src/
│   ├── config.py
│   ├── llm.py
│   ├── vectordata.py
│   │
│   └── state/
│       ├── session_store.py
│       ├── history.py
│       ├── summary.py
│       └── __init__.py
│
├── .env
├── requirements.txt
├── README.md
└── pyproject.toml
```

---

# 🏗️ Architecture

```
                +----------------------+
                |   Streamlit Frontend |
                +----------+-----------+
                           |
                           |
                    HTTP Requests
                           |
                           ▼
                +----------------------+
                |    FastAPI Backend   |
                +----------+-----------+
                           |
          +----------------+----------------+
          |                                 |
          ▼                                 ▼
 Conversation Memory               Retrieval Pipeline
          |                                 |
 Rolling Summary                  Vector Database
          |                                 |
          +----------------+----------------+
                           |
                           ▼
                      LangChain
                           |
                           ▼
                      Groq LLM
                           |
                           ▼
                    AI Generated Answer
```

---

# 📈 Future Improvements

- 🔐 User authentication
- 🌐 Multi-user deployment
- 📄 Support for PDF documentation
- 📊 Repository visualization
- 🧪 Unit and integration testing
- ☁️ Docker & cloud deployment
- 📚 Multi-repository support
- 🔍 Hybrid search (Keyword + Vector Search)
- 🎙️ Voice interaction
- 🤖 Agentic repository exploration

---

# 🤝 Contributing

Contributions are always welcome!

If you'd like to improve this project:

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Commit your changes

```bash
git commit -m "Add awesome feature"
```

4. Push your branch

```bash
git push origin feature/my-feature
```

5. Open a Pull Request 🚀

---

# 📄 License

This project is licensed under the **MIT License**.

Feel free to use, modify, and distribute it in accordance with the license terms.

---

## ⭐ If you found this project useful, consider giving it a star!
