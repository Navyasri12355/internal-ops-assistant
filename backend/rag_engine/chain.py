"""
RAG Chain
---------
Connects the vector store retrieval to the LLM generation step.
Uses LangChain for orchestration with a local Ollama backend.
"""

import os
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


SYSTEM_PROMPT = """You are KnowledgeAgent, an internal AI assistant for a startup.
Your job is to answer employee questions accurately using ONLY the provided context documents.

Rules:
- Answer only from the provided context. Do not use outside knowledge.
- If the context does not contain enough information, say: "I don't have enough information in the current knowledge base to answer this."
- Be concise and direct. Use bullet points where helpful.
- Always mention which document(s) your answer is based on.

Context:
{context}
"""

HUMAN_PROMPT = "{question}"


def build_context_string(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks into a readable context block."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk["metadata"]
        source = meta.get("source", "Unknown")
        page = meta.get("page", "?")
        score = chunk.get("score", 0)
        parts.append(
            f"[Source {i}: {source}, page {page}, relevance {score:.2f}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def get_llm(provider: str, model: str):
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url, temperature=0.1)

    raise ValueError(
        f"Unknown LLM provider: {provider}. Supported provider: ollama"
    )


class RAGChain:
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "ollama")
        model = os.getenv("LLM_MODEL", "gemma4")
        self.llm = get_llm(provider, model)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ])
        self.parser = StrOutputParser()
        self.chain = self.prompt | self.llm | self.parser

    def generate(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        context = build_context_string(chunks)
        return self.chain.invoke({"context": context, "question": question})
