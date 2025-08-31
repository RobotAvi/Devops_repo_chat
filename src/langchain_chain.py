from __future__ import annotations

from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .config import settings


def make_chain() -> ChatOpenAI:
    return ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o-mini", temperature=0.1)


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

