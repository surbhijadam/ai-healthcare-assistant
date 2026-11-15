"""
MediCare AI — RAG Healthcare Knowledge Base & Retrieval Engine
Conforms to FR-04 (RAG Healthcare Knowledge Base), US-02, and NFR-01.2.
Orchestrates document chunking, 384-dim dense embedding generation, pgvector similarity search,
and verified clinical context augmentation for Groq LLM queries.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.schemas.chat import DocumentCitation
from backend.db.models.knowledge import KnowledgeDocument, DocumentChunk
from backend.repositories.knowledge_repo import knowledge_repo
from backend.services.chunking_service import chunking_service
from backend.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

# Authoritative baseline clinical reference guidelines (Pre-seeded for RAG)
BASELINE_GUIDELINES = [
    {
        "title": "ACC/AHA Clinical Guidelines for Blood Cholesterol Management",
        "category": "Cardiovascular Medicine",
        "content": (
            "The American College of Cardiology and American Heart Association guidelines recommend that Low-Density Lipoprotein (LDL) "
            "cholesterol be maintained below 100 mg/dL for general adult health, and below 70 mg/dL for patients with established cardiovascular disease. "
            "High-Density Lipoprotein (HDL) acts as a scavenger carrying cholesterol from peripheral tissues back to the liver; optimal HDL is above 40 mg/dL for men "
            "and above 50 mg/dL for women. Triglycerides should remain below 150 mg/dL. Non-pharmacological interventions include diets rich in soluble fiber, "
            "reduction in trans-fat and saturated fatty acids, regular aerobic physical exercise (at least 150 minutes weekly), and weight management."
        )
    },
    {
        "title": "ADA Standards of Medical Care in Diabetes: Glucose and HbA1c Targets",
        "category": "Endocrinology",
        "content": (
            "The American Diabetes Association (ADA) establishes diagnostic reference criteria for glycemic control: "
            "Fasting plasma glucose (FPG) between 70 and 99 mg/dL is considered normal. Impaired fasting glucose (prediabetes) is defined as 100 to 125 mg/dL. "
            "A fasting glucose of 126 mg/dL or higher on two separate occasions indicates diabetes. "
            "Hemoglobin A1c (HbA1c) measures average blood glucose over 2 to 3 months: normal is below 5.7%; prediabetes is 5.7% to 6.4%; "
            "and 6.5% or greater is diagnostic for diabetes. For non-pregnant adults with diabetes, a general HbA1c target of under 7.0% is widely recommended."
        )
    },
    {
        "title": "AHA/ACC Hypertension Clinical Practice Guidelines: Blood Pressure Targets",
        "category": "Cardiovascular Medicine",
        "content": (
            "According to the AHA/ACC clinical practice guidelines, adult blood pressure is categorized into four distinct tiers: "
            "1. Normal: Systolic under 120 mmHg AND diastolic under 80 mmHg. "
            "2. Elevated: Systolic 120-129 mmHg AND diastolic under 80 mmHg. "
            "3. Stage 1 Hypertension: Systolic 130-139 mmHg OR diastolic 80-89 mmHg. "
            "4. Stage 2 Hypertension: Systolic 140 mmHg or greater OR diastolic 90 mmHg or greater. "
            "Hypertensive crisis occurs when readings exceed 180/120 mmHg, requiring immediate emergency medical evaluation if accompanied by organ damage symptoms."
        )
    },
    {
        "title": "GINA Global Strategy for Asthma Management and Inhaler Protocol",
        "category": "Pulmonology",
        "content": (
            "The Global Initiative for Asthma (GINA) classifies asthma therapies into two fundamental categories: "
            "Daily controller medications (primarily low-dose Inhaled Corticosteroids / ICS) reduce airway inflammation, decrease bronchial hyper-responsiveness, "
            "and prevent exacerbations. As-needed rescue or reliever inhalers (such as Short-Acting Beta-2 Agonists / SABA or ICS-formoterol) rapidly dilate bronchial smooth muscle "
            "to alleviate acute symptoms such as shortness of breath, chest tightness, and wheezing. Patients should never discontinue maintenance controllers abruptly."
        )
    }
]


class HealthcareRAGService:
    """Orchestrates ingestion, vector embedding, and source-grounded context augmentation."""

    def __init__(self):
        self.chunker = chunking_service
        self.embedder = embedding_service

    async def ingest_document(
        self,
        session: AsyncSession,
        title: str,
        content: str,
        category: str = "Clinical Guideline",
        source_url: Optional[str] = None,
        uploaded_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Ingests clinical reference document into PostgreSQL pgvector knowledge base (FR-04.1 - FR-04.3).
        1. Creates KnowledgeDocument record
        2. Splits text into 500-token semantic chunks with 50-token overlap
        3. Computes 384-dim dense embeddings
        4. Persists chunks with pgvector embeddings
        """
        # 1. Create document
        doc = await knowledge_repo.create_document(
            session=session,
            title=title,
            category=category,
            source_url=source_url,
            uploaded_by=uploaded_by
        )

        # 2. Chunk text
        chunks = self.chunker.chunk_text(content, document_title=title)
        if not chunks:
            chunks = [{
                "chunk_index": 0,
                "chunk_text": content.strip(),
                "metadata": {"document_title": title, "chunk_index": 0}
            }]

        # 3. Compute 384-dim embeddings
        chunks_payload = []
        for c in chunks:
            emb = self.embedder.generate_embedding(c["chunk_text"])
            chunks_payload.append({
                "chunk_index": c["chunk_index"],
                "chunk_text": c["chunk_text"],
                "embedding": emb,
                "metadata": c.get("metadata", {})
            })

        # 4. Save chunks
        created_chunks = await knowledge_repo.add_chunks(
            session=session,
            document_id=doc.id,
            chunks_data=chunks_payload
        )
        await session.commit()

        return {
            "document_id": doc.id,
            "title": doc.title,
            "category": doc.category,
            "total_chunks": len(created_chunks)
        }

    async def retrieve_relevant_context(
        self,
        session: AsyncSession,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.25
    ) -> Dict[str, Any]:
        """
        Retrieves top-k closest clinical chunks for medical query (FR-04.4 / US-02).
        Supports native pgvector cosine search and resilient SQLite fallback.
        """
        query_vec = self.embedder.generate_embedding(query)
        citations: List[DocumentCitation] = []
        context_chunks: List[str] = []

        try:
            # Attempt pgvector native HNSW cosine distance search (<=>)
            results = await knowledge_repo.search_similar_chunks(
                session=session,
                query_embedding=query_vec,
                top_k=top_k
            )

            for chunk, sim in results:
                if sim >= min_similarity:
                    doc_title = chunk.document.title if chunk.document else "Clinical Care Guideline"
                    citations.append(
                        DocumentCitation(
                            document_title=doc_title,
                            chunk_id=chunk.id,
                            similarity_score=sim
                        )
                    )
                    context_chunks.append(f"[{doc_title}]: {chunk.chunk_text}")

            if context_chunks:
                return {
                    "rag_context": "\n\n".join(context_chunks),
                    "citations": citations
                }
        except Exception as e:
            logger.debug(f"Native pgvector search skipped or unavailable ({e}); utilizing in-memory RAG fallback.")

        # Fallback in-memory search over baseline authoritative guidelines
        scored_guidelines = []
        for g in BASELINE_GUIDELINES:
            g_vec = self.embedder.generate_embedding(g["content"])
            sim = self.embedder.compute_cosine_similarity(query_vec, g_vec)
            scored_guidelines.append((g, round(sim, 4)))

        # Sort by similarity descending
        scored_guidelines.sort(key=lambda x: x[1], reverse=True)

        for g, sim in scored_guidelines[:top_k]:
            if sim >= min_similarity or len(citations) == 0:
                citations.append(
                    DocumentCitation(
                        document_title=g["title"],
                        chunk_id=None,
                        similarity_score=sim
                    )
                )
                context_chunks.append(f"[{g['title']}]: {g['content']}")

        return {
            "rag_context": "\n\n".join(context_chunks) if context_chunks else None,
            "citations": citations
        }

    async def seed_baseline_knowledge(self, session: AsyncSession):
        """Seeds authoritative baseline medical guidelines into knowledge base if empty."""
        try:
            # Check existing document count
            stmt = select(KnowledgeDocument)
            existing = (await session.execute(stmt)).scalars().first()
            if not existing:
                for guideline in BASELINE_GUIDELINES:
                    await self.ingest_document(
                        session=session,
                        title=guideline["title"],
                        content=guideline["content"],
                        category=guideline["category"]
                    )
                logger.info("Authoritative baseline RAG guidelines seeded successfully.")
        except Exception as e:
            logger.warning(f"Knowledge base seeding skipped: {e}")


# Global singleton instance
rag_service = HealthcareRAGService()
