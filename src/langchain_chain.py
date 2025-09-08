from __future__ import annotations

from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .config import settings


def make_chain() -> ChatOpenAI:
    api_key = settings.llm_api_key or settings.openai_api_key
    base_url = settings.llm_base_url
    model = settings.llm_model
    return ChatOpenAI(api_key=api_key, base_url=base_url, model=model, temperature=0.1)


def generate_answer(question: str, context_chunks: List[str]) -> str:
    prompt = ChatPromptTemplate.from_template(
        """
You are a helpful software assistant answering questions about one or more GitLab repositories.
Use the provided context to answer concisely in Russian. If the answer is not in the context, say you don't have enough information.

Question:
{question}

Context:
{context}

Answer in Russian.
        """
    )
    chain = make_chain()
    context = "\n\n".join(context_chunks[:8])
    msg = prompt.format_messages(question=question, context=context)
    out = chain.invoke(msg)
    return out.content.strip()

