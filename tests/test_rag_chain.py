"""Tests for the RAG chain module."""

import pytest
from unittest.mock import MagicMock, patch


class TestBuildContextString:
    def test_formats_single_chunk(self):
        from backend.rag_engine.chain import build_context_string

        chunks = [{
            "content": "Employees get 24 days leave.",
            "metadata": {"source": "handbook.pdf", "page": 3},
            "score": 0.91,
        }]
        result = build_context_string(chunks)
        assert "handbook.pdf" in result
        assert "page 3" in result
        assert "0.91" in result
        assert "Employees get 24 days leave." in result

    def test_formats_multiple_chunks_with_separator(self):
        from backend.rag_engine.chain import build_context_string

        chunks = [
            {"content": "Chunk A", "metadata": {"source": "a.pdf", "page": 1}, "score": 0.9},
            {"content": "Chunk B", "metadata": {"source": "b.pdf", "page": 2}, "score": 0.8},
        ]
        result = build_context_string(chunks)
        assert "Chunk A" in result
        assert "Chunk B" in result
        assert "---" in result  # separator between chunks

    def test_handles_missing_metadata_keys(self):
        """Should not crash when metadata keys are absent."""
        from backend.rag_engine.chain import build_context_string

        chunks = [{"content": "text", "metadata": {}, "score": 0.5}]
        result = build_context_string(chunks)
        assert "text" in result
        assert "Unknown" in result  # fallback for missing source

    def test_chunk_numbering_starts_at_1(self):
        from backend.rag_engine.chain import build_context_string

        chunks = [{"content": "x", "metadata": {"source": "s", "page": 1}, "score": 0.5}]
        result = build_context_string(chunks)
        assert "Source 1:" in result


class TestGetLLM:
    def test_ollama_returns_chat_ollama(self):
        with patch("backend.rag_engine.chain.ChatOllama") as MockOllama:
            from backend.rag_engine.chain import get_llm
            get_llm("ollama", "gemma4")
            MockOllama.assert_called_once()

    def test_unknown_provider_raises_value_error(self):
        from backend.rag_engine.chain import get_llm
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_llm("openai", "gpt-4")


class TestRAGChain:
    def test_generate_invokes_chain(self):
        with patch("backend.rag_engine.chain.get_llm") as mock_get_llm, \
             patch("backend.rag_engine.chain.ChatPromptTemplate") as MockPrompt, \
             patch("backend.rag_engine.chain.StrOutputParser") as MockParser:

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "The answer is 42."

            # Make prompt | llm | parser chain work
            mock_prompt_instance = MagicMock()
            MockPrompt.from_messages.return_value = mock_prompt_instance
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_chain.__or__ = MagicMock(return_value=mock_chain)

            from backend.rag_engine.chain import RAGChain
            rag = RAGChain()
            rag.chain = mock_chain

            result = rag.generate("What is the leave policy?", [
                {"content": "24 days leave.", "metadata": {"source": "hr.pdf", "page": 1}, "score": 0.9}
            ])

            mock_chain.invoke.assert_called_once()
            assert result == "The answer is 42."

    def test_generate_passes_question_and_context(self):
        with patch("backend.rag_engine.chain.get_llm"):
            from backend.rag_engine.chain import RAGChain
            rag = RAGChain()
            rag.chain = MagicMock(return_value="answer")

            chunks = [{"content": "policy text", "metadata": {"source": "doc.pdf", "page": 1}, "score": 0.88}]
            rag.generate("What is the policy?", chunks)

            call_args = rag.chain.invoke.call_args[0][0]
            assert "What is the policy?" in call_args["question"]
            assert "policy text" in call_args["context"]