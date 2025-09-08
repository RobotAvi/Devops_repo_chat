from __future__ import annotations

from typing import List

from langchain_openai import OpenAIEmbeddings

from .config import settings


def get_embeddings() -> OpenAIEmbeddings:
    api_key = settings.embedding_api_key or settings.openai_api_key or settings.llm_api_key
    base_url = settings.embedding_base_url or settings.llm_base_url
    return OpenAIEmbeddings(api_key=api_key, base_url=base_url, model=settings.embedding_model)


def embed_texts(texts: List[str]) -> List[List[float]]:
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)

