from support_agent.ingest import Document, chunk_document, load_documents


def test_load_documents_has_titles():
    docs = load_documents()
    assert len(docs) >= 20
    assert all(d.title and d.text for d in docs)


def test_chunking_overlap_and_coverage():
    doc = Document(doc_id="d", title="T", text=" ".join(f"w{i}" for i in range(200)))
    chunks = chunk_document(doc, chunk_words=80, overlap=20)
    assert [c.chunk_id for c in chunks] == ["d#0", "d#1", "d#2"]
    assert chunks[1].text.split()[1] == "w60"  # starts after title, 60-word step
    assert "w199" in chunks[-1].text


def test_short_document_single_chunk():
    doc = Document(doc_id="d", title="T", text="only a few words")
    assert len(chunk_document(doc)) == 1
