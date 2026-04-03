"""
Document Ingestor
-----------------
Parses and chunks documents from various formats (PDF, Markdown, DOCX, plain text).
Each chunk is stored with metadata: source filename, page number, chunk index.
"""

import os
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_pdf(filepath: str) -> List[Dict[str, Any]]:
    doc = fitz.open(filepath)
    pages = []
    for page_num, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append({
                "content": text,
                "metadata": {
                    "source": Path(filepath).name,
                    "page": page_num + 1,
                    "filetype": "pdf",
                }
            })
    doc.close()
    return pages


def load_markdown(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return [{"content": content, "metadata": {"source": Path(filepath).name, "page": 1, "filetype": "markdown"}}]


def load_docx(filepath: str) -> List[Dict[str, Any]]:
    doc = docx.Document(filepath)
    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    return [{"content": text, "metadata": {"source": Path(filepath).name, "page": 1, "filetype": "docx"}}]


def load_txt(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return [{"content": content, "metadata": {"source": Path(filepath).name, "page": 1, "filetype": "txt"}}]


LOADERS = {".pdf": load_pdf, ".md": load_markdown, ".markdown": load_markdown, ".docx": load_docx, ".txt": load_txt}


def load_document(filepath: str) -> List[Dict[str, Any]]:
    ext = Path(filepath).suffix.lower()
    loader = LOADERS.get(ext)
    if not loader:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader(filepath)


def chunk_documents(docs: List[Dict[str, Any]], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict[str, Any]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for doc in docs:
        splits = splitter.split_text(doc["content"])
        for i, split in enumerate(splits):
            chunks.append({"content": split, "metadata": {**doc["metadata"], "chunk_index": i}})
    return chunks


def ingest_directory(directory: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict[str, Any]]:
    all_chunks = []
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = Path(filepath).suffix.lower()
            if ext in LOADERS:
                print(f"  Loading: {filename}")
                try:
                    docs = load_document(filepath)
                    chunks = chunk_documents(docs, chunk_size, chunk_overlap)
                    all_chunks.extend(chunks)
                    print(f"    -> {len(chunks)} chunks")
                except Exception as e:
                    print(f"    Failed: {e}")
    return all_chunks
