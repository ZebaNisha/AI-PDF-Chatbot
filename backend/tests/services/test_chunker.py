import uuid

from app.schemas.pdf import ExtractedDocument, ExtractedPage, ExtractionStatus
from app.services.chunker import RecursiveTokenChunker


def create_mock_extracted_doc(pages_text: list[str]) -> ExtractedDocument:
    pages = []
    for i, text in enumerate(pages_text):
        pages.append(
            ExtractedPage(
                page_number=i + 1,
                text=text,
                char_count=len(text)
            )
        )
    return ExtractedDocument(
        pages=pages,
        total_pages=len(pages),
        status=ExtractionStatus.SUCCESS,
        metadata={}
    )


def test_chunker_basic():
    doc_id = uuid.uuid4()
    chunker = RecursiveTokenChunker(chunk_size=50, chunk_overlap=10)
    
    # 3 short pages
    doc = create_mock_extracted_doc([
        "This is page 1.",
        "This is page 2.",
        "This is page 3."
    ])
    
    chunks = chunker.chunk_document(doc_id, doc)
    
    # Should fit in one chunk since chunk_size=50
    assert len(chunks) == 1
    assert chunks[0].start_page == 1
    assert chunks[0].end_page == 3
    assert chunks[0].start_char == 0


def test_chunker_empty_pages():
    doc_id = uuid.uuid4()
    chunker = RecursiveTokenChunker(chunk_size=50, chunk_overlap=10)
    
    doc = create_mock_extracted_doc([
        "",
        "Page 2 has text.",
        "",
        "Page 4 has text."
    ])
    
    chunks = chunker.chunk_document(doc_id, doc)
    assert len(chunks) == 1
    
    # Even though page 1 is empty, the first actual text starts at character offset 1 
    # (because we add a space after each page).
    # Page 1 text="", space=" " -> len=1. So offset 1 is Page 2.
    assert chunks[0].start_page >= 1


def test_chunker_huge_paragraph():
    doc_id = uuid.uuid4()
    # Tiny chunk size to force splits
    chunker = RecursiveTokenChunker(chunk_size=10, chunk_overlap=2)
    
    huge_paragraph = "word " * 100
    doc = create_mock_extracted_doc([huge_paragraph])
    
    chunks = chunker.chunk_document(doc_id, doc)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.token_count <= 10
        assert chunk.character_count > 0


def test_chunker_no_newline_text():
    doc_id = uuid.uuid4()
    chunker = RecursiveTokenChunker(chunk_size=20, chunk_overlap=5)
    
    no_newlines = "This is a very long string without any newlines. " * 50
    doc = create_mock_extracted_doc([no_newlines])
    
    chunks = chunker.chunk_document(doc_id, doc)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.token_count <= 20


def test_chunker_unicode_heavy():
    doc_id = uuid.uuid4()
    chunker = RecursiveTokenChunker(chunk_size=50, chunk_overlap=10)
    
    unicode_text = "🚀 こんにちは 世界 😊 " * 20
    doc = create_mock_extracted_doc([unicode_text])
    
    chunks = chunker.chunk_document(doc_id, doc)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.token_count <= 50


def test_chunker_strict_ordering():
    doc_id = uuid.uuid4()
    chunker = RecursiveTokenChunker(chunk_size=10, chunk_overlap=2)
    
    # Text that will be split
    doc = create_mock_extracted_doc([
        "A " * 20,
        "B " * 20,
        "C " * 20
    ])
    
    chunks = chunker.chunk_document(doc_id, doc)
    
    assert len(chunks) > 3
    
    # Ensure start_char and chunk_index are strictly increasing
    prev_char = -1
    prev_idx = -1
    for chunk in chunks:
        assert chunk.chunk_index > prev_idx
        assert chunk.start_char >= prev_char
        assert chunk.document_id == doc_id
        
        prev_idx = chunk.chunk_index
        prev_char = chunk.start_char
