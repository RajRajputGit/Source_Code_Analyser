import os
from git import Repo
from langchain_community.document_loaders.parsers.language.language_parser import (
    Language,
)
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.document_loaders.generic import GenericLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def create_vectordata(
    url: str,
    path: str,
    language: str = "python",
    embedding_model: str = "all-MiniLM-L6-v2",
    persist_directory: str = "../vectordata",
):

    # If `path` already exists and is a non-empty git checkout, reuse it.
    # Otherwise `git clone` aborts with "destination path already exists and
    # is not an empty directory", which breaks the API on every restart.
    if os.path.isdir(path) and os.path.isdir(os.path.join(path, ".git")):
        repo = Repo(path)
    else:
        repo = Repo.clone_from(url, to_path=path)

    parser = LanguageParser(language=language, parser_threshold=500)

    loader = GenericLoader.from_filesystem(
        path, glob="**/*", suffixes=[".py"], parser=parser
    )

    documents = loader.load()

    document_splitter = RecursiveCharacterTextSplitter.from_language(
        language="python", chunk_size=500, chunk_overlap=20
    )

    splitted_docs = document_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vecotordb = Chroma.from_documents(
        splitted_docs, embedding=embeddings, persist_directory=persist_directory
    )

    return embeddings, vecotordb
