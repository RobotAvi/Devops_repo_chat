from __future__ import annotations

from typing import List

from langchain_openai import OpenAIEmbeddings

from .config import settings


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(api_key=settings.openai_api_key, model=settings.embedding_model)


def embed_texts(texts: List[str]) -> List[List[float]]:
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)

