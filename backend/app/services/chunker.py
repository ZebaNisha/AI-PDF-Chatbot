import uuid
from typing import List, Tuple

import tiktoken

from app.schemas.chunk import DocumentChunk
from app.schemas.pdf import ExtractedDocument
from app.utils.token_counter import count_tokens, encoding

class RecursiveTokenChunker:
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " "]

    def _get_page_for_offset(self, offset: int, page_map: List[Tuple[int, int, int]]) -> int:
        for start, end, page_num in page_map:
            if start <= offset < end:
                return page_num
        if page_map:
            return page_map[-1][2]
        return 1

    def _split_text(self, text: str, global_offset: int) -> List[Tuple[str, int, int]]:
        """
        Recursively split text. Returns list of (chunk_text, start_global, end_global)
        """
        if count_tokens(text) <= self.chunk_size:
            return [(text, global_offset, global_offset + len(text))]

        for sep in self.separators:
            if sep in text:
                splits = text.split(sep)
                chunks = []
                current_chunk = ""
                current_start = global_offset
                
                # Split with this separator
                for i, split in enumerate(splits):
                    part = split + sep if i < len(splits) - 1 else split
                    
                    if not current_chunk:
                        current_chunk = part
                    else:
                        if count_tokens(current_chunk + part) <= self.chunk_size:
                            current_chunk += part
                        else:
                            # Flush current_chunk
                            end_idx = current_start + len(current_chunk)
                            chunks.append((current_chunk, current_start, end_idx))
                            
                            # Start next chunk with overlap
                            # We need to backtrack by `chunk_overlap` tokens.
                            # But since we are building recursively, a simpler overlap mechanism
                            # is to just include previous text up to the overlap limit.
                            
                            encoded = encoding.encode(current_chunk)
                            if len(encoded) > self.chunk_overlap:
                                overlap_tokens = encoded[-self.chunk_overlap:]
                                overlap_text = encoding.decode(overlap_tokens)
                                # Find where overlap_text actually starts in current_chunk
                                overlap_idx = current_chunk.rfind(overlap_text[:10]) 
                                if overlap_idx == -1:
                                    overlap_idx = len(current_chunk) // 2 # Fallback approximation
                            else:
                                overlap_text = current_chunk
                                overlap_idx = 0
                                
                            current_start = current_start + overlap_idx
                            current_chunk = current_chunk[overlap_idx:] + part

                if current_chunk:
                    end_idx = current_start + len(current_chunk)
                    chunks.append((current_chunk, current_start, end_idx))
                
                # Check if all resulting chunks are small enough
                # If they are, we succeeded. If not, we fall through to the next separator.
                if all(count_tokens(c[0]) <= self.chunk_size for c in chunks):
                    return chunks

        # Fallback: Hard split by tokens
        encoded = encoding.encode(text)
        chunks = []
        current_idx = 0
        current_global = global_offset
        
        while current_idx < len(encoded):
            end_idx = min(current_idx + self.chunk_size, len(encoded))
            chunk_tokens = encoded[current_idx:end_idx]
            chunk_text = encoding.decode(chunk_tokens)
            
            chunk_end_global = current_global + len(chunk_text)
            chunks.append((chunk_text, current_global, chunk_end_global))
            
            current_idx += (self.chunk_size - self.chunk_overlap)
            current_global += len(encoding.decode(encoded[current_idx:end_idx])) # approx

        return chunks


    def chunk_document(self, document_id: uuid.UUID, extracted_doc: ExtractedDocument) -> List[DocumentChunk]:
        full_text = ""
        page_map: List[Tuple[int, int, int]] = []  # (start_char, end_char, page_number)
        
        current_offset = 0
        for page in extracted_doc.pages:
            # We add a space between pages to ensure words don't merge
            page_text = page.text + " "
            page_len = len(page_text)
            
            page_map.append((current_offset, current_offset + page_len, page.page_number))
            full_text += page_text
            current_offset += page_len
            
        full_text = full_text.strip()
        
        raw_chunks = self._split_text(full_text, 0)
        
        document_chunks = []
        for i, (text, start_char, end_char) in enumerate(raw_chunks):
            start_page = self._get_page_for_offset(start_char, page_map)
            end_page = self._get_page_for_offset(end_char - 1, page_map) if end_char > start_char else start_page
            
            document_chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=i,
                    text=text.strip(),
                    start_page=start_page,
                    end_page=end_page,
                    start_char=start_char,
                    end_char=end_char,
                    token_count=count_tokens(text),
                    character_count=len(text),
                    metadata={}
                )
            )
            
        return document_chunks
