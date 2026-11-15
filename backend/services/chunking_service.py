"""
MediCare AI — Semantic Document Chunking Service
Conforms to FR-04.2 (Recursive semantic chunks of 500 tokens with 50-token overlap).
Splits clinical texts at natural sentence and paragraph boundaries to preserve medical context.
"""

import re
from typing import List, Dict, Any, Optional


class SemanticChunkingService:
    """Recursively splits medical documents into overlapping semantic chunks."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        document_title: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Splits text into chunks of target size with specified overlap.
        Respects paragraph and sentence boundaries.
        """
        text = text.strip()
        if not text:
            return []

        # Split into initial paragraphs
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

        # Break paragraphs into sentence units
        sentence_units = []
        for p in paragraphs:
            # Match sentence terminals (. ! ?) followed by space or newline
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for s in sentences:
                s_clean = s.strip()
                if s_clean:
                    sentence_units.append(s_clean)

        chunks: List[Dict[str, Any]] = []
        current_chunk_sentences: List[str] = []
        current_word_count = 0
        chunk_idx = 0

        for sentence in sentence_units:
            s_words = len(sentence.split())
            if current_word_count + s_words > self.chunk_size and current_chunk_sentences:
                # Flush current chunk
                chunk_str = " ".join(current_chunk_sentences).strip()
                chunks.append({
                    "chunk_index": chunk_idx,
                    "chunk_text": chunk_str,
                    "word_count": len(chunk_str.split()),
                    "metadata": {
                        "document_title": document_title or "Clinical Guideline",
                        "chunk_index": chunk_idx
                    }
                })
                chunk_idx += 1

                # Maintain overlap by retaining trailing sentences
                overlap_sentences = []
                overlap_words = 0
                for rev_s in reversed(current_chunk_sentences):
                    rw = len(rev_s.split())
                    if overlap_words + rw <= self.chunk_overlap:
                        overlap_sentences.insert(0, rev_s)
                        overlap_words += rw
                    else:
                        break

                current_chunk_sentences = overlap_sentences
                current_word_count = overlap_words

            current_chunk_sentences.append(sentence)
            current_word_count += s_words

        # Append final remainder chunk
        if current_chunk_sentences:
            chunk_str = " ".join(current_chunk_sentences).strip()
            chunks.append({
                "chunk_index": chunk_idx,
                "chunk_text": chunk_str,
                "word_count": len(chunk_str.split()),
                "metadata": {
                    "document_title": document_title or "Clinical Guideline",
                    "chunk_index": chunk_idx
                }
            })

        return chunks


# Global singleton instance
chunking_service = SemanticChunkingService()
