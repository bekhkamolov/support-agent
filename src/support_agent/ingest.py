"""Load the policy documents and split them into overlapping chunks."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from .config import POLICY_DIR


class Document(BaseModel):
    doc_id: str
    title: str
    text: str


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    text: str


def load_documents(policy_dir: Path = POLICY_DIR) -> list[Document]:
    docs = []
    for path in sorted(policy_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8").strip()
        lines = raw.splitlines()
        title = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("#") else path.stem
        body = "\n".join(lines[1:]).strip() if lines and lines[0].startswith("#") else raw
        docs.append(Document(doc_id=path.stem, title=title, text=body))
    if not docs:
        raise FileNotFoundError(f"No .md documents found in {policy_dir}")
    return docs


def chunk_document(doc: Document, chunk_words: int = 80, overlap: int = 20) -> list[Chunk]:
    """Split a document into word windows with overlap.

    The title is prepended to every chunk so that short chunks keep their topic.
    """
    if overlap >= chunk_words:
        raise ValueError("overlap must be smaller than chunk_words")
    words = doc.text.split()
    step = chunk_words - overlap
    chunks = []
    for i, start in enumerate(range(0, max(len(words), 1), step)):
        window = words[start : start + chunk_words]
        if not window:
            break
        chunks.append(
            Chunk(
                chunk_id=f"{doc.doc_id}#{i}",
                doc_id=doc.doc_id,
                title=doc.title,
                text=f"{doc.title}. " + " ".join(window),
            )
        )
        if start + chunk_words >= len(words):
            break
    return chunks


def build_chunks(chunk_words: int = 80, overlap: int = 20) -> list[Chunk]:
    return [c for d in load_documents() for c in chunk_document(d, chunk_words, overlap)]
