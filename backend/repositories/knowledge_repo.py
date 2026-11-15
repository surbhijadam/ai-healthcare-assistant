from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.knowledge import KnowledgeDocument, DocumentChunk
from backend.repositories.base import BaseRepository


class KnowledgeRepository(BaseRepository[KnowledgeDocument]):
    """Repository managing clinical knowledge documents and pgvector semantic retrieval (FR-04.1 - FR-04.5)."""

    def __init__(self):
        super().__init__(KnowledgeDocument)

    async def create_document(
        self,
        session: AsyncSession,
        title: str,
        category: str = "Clinical Guideline",
        source_url: Optional[str] = None,
        uploaded_by: Optional[int] = None,
    ) -> KnowledgeDocument:
        doc = KnowledgeDocument(
            title=title,
            category=category,
            source_url=source_url,
            uploaded_by=uploaded_by,
            status="Reviewed"
        )
        session.add(doc)
        await session.flush()
        await session.refresh(doc)
        return doc

    async def add_chunks(
        self,
        session: AsyncSession,
        document_id: int,
        chunks_data: List[Dict[str, Any]],
    ) -> List[DocumentChunk]:
        created_chunks: List[DocumentChunk] = []
        for idx, chunk_info in enumerate(chunks_data):
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk_info.get("chunk_index", idx),
                chunk_text=chunk_info["chunk_text"],
                embedding=chunk_info["embedding"],
                metadata_json=chunk_info.get("metadata", {}),
            )
            session.add(chunk)
            created_chunks.append(chunk)

        await session.flush()
        return created_chunks

    async def search_similar_chunks(
        self,
        session: AsyncSession,
        query_embedding: List[float],
        top_k: int = 3,
    ) -> List[Tuple[DocumentChunk, float]]:
        """Retrieves top-k closest document chunks using pgvector HNSW cosine distance (<=>). (NFR-01.2)."""
        try:
            # In PostgreSQL with pgvector, cosine_distance produces distance in [0, 2]
            # Similarity score = 1.0 - cosine_distance
            distance_expr = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")

            stmt = (
                select(DocumentChunk, distance_expr)
                .options(selectinload(DocumentChunk.document))
                .order_by(distance_expr.asc())
                .limit(top_k)
            )

            result = await session.execute(stmt)
            items: List[Tuple[DocumentChunk, float]] = []
            for chunk, dist in result.all():
                similarity = max(0.0, min(1.0, 1.0 - float(dist)))
                items.append((chunk, round(similarity, 4)))

            return items
        except Exception:
            # Resilient fallback (e.g. SQLite / in-memory or environment without pgvector extension loaded)
            from backend.services.embedding_service import embedding_service
            stmt = select(DocumentChunk).options(selectinload(DocumentChunk.document))
            result = await session.execute(stmt)
            all_chunks = list(result.scalars().all())
            if not all_chunks:
                return []

            scored = []
            for chunk in all_chunks:
                chunk_emb = chunk.embedding
                if isinstance(chunk_emb, (list, tuple)) or hasattr(chunk_emb, "__iter__"):
                    emb_list = list(chunk_emb)
                else:
                    emb_list = [0.0] * len(query_embedding)
                sim = embedding_service.compute_cosine_similarity(query_embedding, emb_list)
                scored.append((chunk, round(sim, 4)))

            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:top_k]


knowledge_repo = KnowledgeRepository()
