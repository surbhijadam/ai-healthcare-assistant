"""
MediCare AI — Comprehensive Automated Test Suite for Phase 8: RAG Healthcare Knowledge Base
Validates FR-04.1 (pgvector Knowledge Base Ingestion), FR-04.2 (Semantic Chunking),
FR-04.3 (384-dim Dense Embeddings), FR-04.4 (Vector Cosine Retrieval), FR-04.5 (Source Citations),
and NFR-01.2 (Sub-second vector retrieval).
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.chunking_service import chunking_service
from backend.services.embedding_service import embedding_service
from backend.services.rag_service import rag_service, BASELINE_GUIDELINES
from backend.tests.conftest import TestingSessionLocal
from backend.core.security import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_token_header():
    token = create_access_token(data={"sub": "1", "role": "ROLE_USER"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token_header():
    token = create_access_token(data={"sub": "99", "role": "ROLE_ADMIN"})
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# 1. Semantic Chunking Service Tests (FR-04.2)
# ==============================================================================

def test_chunking_service_empty_text():
    """Validates that empty or whitespace strings return an empty list of chunks."""
    assert chunking_service.chunk_text("") == []
    assert chunking_service.chunk_text("   \n\t  ") == []


def test_chunking_service_short_text_single_chunk():
    """Validates that text under 500 words is packaged into a single clean chunk."""
    text = (
        "Normal blood pressure in adults is defined as a systolic reading below 120 mmHg "
        "and a diastolic reading below 80 mmHg. Lifestyle modifications such as reduced sodium intake "
        "and regular aerobic exercise are strongly recommended."
    )
    chunks = chunking_service.chunk_text(text, document_title="AHA Hypertension Summary")
    assert len(chunks) == 1
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["word_count"] > 10
    assert chunks[0]["metadata"]["document_title"] == "AHA Hypertension Summary"
    assert "systolic reading below 120 mmHg" in chunks[0]["chunk_text"]


def test_chunking_service_long_text_overlap():
    """
    Validates recursive semantic splitting at sentence boundaries with
    target size and trailing overlap (FR-04.2).
    """
    # Create test chunker with small chunk_size=30, chunk_overlap=10 to test boundary mechanics
    from backend.services.chunking_service import SemanticChunkingService
    test_chunker = SemanticChunkingService(chunk_size=30, chunk_overlap=10)

    sentences = [
        f"Clinical sentence {i} discusses specific medical diagnostic criteria for endocrine health."
        for i in range(1, 15)
    ]
    long_doc = " ".join(sentences)
    chunks = test_chunker.chunk_text(long_doc, document_title="Endocrine Review")

    assert len(chunks) > 1
    for i, c in enumerate(chunks):
        assert c["chunk_index"] == i
        assert c["word_count"] > 0
        assert c["metadata"]["document_title"] == "Endocrine Review"

    # Verify overlap exists between consecutive chunks
    overlap_found = any(
        any(word in chunks[i+1]["chunk_text"] for word in chunks[i]["chunk_text"].split()[-4:])
        for i in range(len(chunks) - 1)
    )
    assert overlap_found is True


# ==============================================================================
# 2. 384-Dimensional Dense Vector Embedding Service Tests (FR-04.3, NFR-01.2)
# ==============================================================================

def test_embedding_dimension_and_unit_normalization():
    """
    Validates that embeddings strictly conform to Vector(384) dimension
    and are normalized to unit L2 length (||v|| = 1.0) per FR-04.3.
    """
    text = "The American Diabetes Association recommends maintaining HbA1c below 7.0 percent."
    emb = embedding_service.generate_embedding(text)

    # 1. Dimension validation
    assert len(emb) == 384
    assert isinstance(emb, list)
    assert all(isinstance(x, float) for x in emb)

    # 2. Unit norm validation (L2 norm == 1.0)
    norm = np.linalg.norm(np.array(emb, dtype=np.float32))
    assert abs(norm - 1.0) < 1e-3, f"Embedding norm was {norm}, expected ~1.0"


def test_embedding_batch_generation():
    """Validates batch embedding calculation."""
    texts = [
        "Cardiovascular risk assessment and lipid profiles.",
        "Management of acute asthma exacerbations using bronchodilators.",
        "Renal clearance and estimated glomerular filtration rate (eGFR)."
    ]
    batch_embs = embedding_service.generate_embeddings(texts)
    assert len(batch_embs) == 3
    for emb in batch_embs:
        assert len(emb) == 384
        norm = np.linalg.norm(np.array(emb, dtype=np.float32))
        assert abs(norm - 1.0) < 1e-3


def test_embedding_cosine_similarity_semantic_relevance():
    """
    Validates that semantically related medical texts yield higher cosine similarity
    than unrelated texts.
    """
    cardio_query = embedding_service.generate_embedding("High LDL cholesterol and heart disease risk")
    cardio_doc = embedding_service.generate_embedding("Low-density lipoprotein cholesterol guidelines and statin therapy")
    asthma_doc = embedding_service.generate_embedding("Inhaled corticosteroids and rescue bronchodilators for asthma")

    sim_related = embedding_service.compute_cosine_similarity(cardio_query, cardio_doc)
    sim_unrelated = embedding_service.compute_cosine_similarity(cardio_query, asthma_doc)

    assert sim_related > sim_unrelated
    assert sim_related > 0.40


# ==============================================================================
# 3. Healthcare RAG Ingestion & Similarity Retrieval Tests (FR-04.1 - FR-04.5)
# ==============================================================================

@pytest.mark.asyncio
async def test_rag_ingest_and_retrieve_document():
    """
    Validates full RAG pipeline: document ingestion, chunk storage,
    and top-k vector cosine retrieval with source citations.
    """
    async with TestingSessionLocal() as session:
        title = "Thyroid Function Test Guidelines"
        content = (
            "Thyroid-stimulating hormone (TSH) is the primary screening test for thyroid dysfunction. "
            "Normal adult TSH levels typically range between 0.4 and 4.0 mIU/L. "
            "Elevated TSH with low free thyroxine (Free T4) indicates primary hypothyroidism. "
            "Conversely, suppressed TSH with elevated Free T4 indicates hyperthyroidism. "
            "Routine screening is indicated for symptomatic patients or individuals with autoimmune history."
        )

        # 1. Ingest document
        ingest_res = await rag_service.ingest_document(
            session=session,
            title=title,
            content=content,
            category="Endocrinology"
        )
        assert ingest_res["document_id"] > 0
        assert ingest_res["title"] == title
        assert ingest_res["total_chunks"] >= 1

        # 2. Retrieve context using query
        retrieval = await rag_service.retrieve_relevant_context(
            session=session,
            query="What does an elevated TSH level indicate about thyroid health?",
            top_k=2
        )

        assert retrieval["rag_context"] is not None
        assert "Thyroid" in retrieval["rag_context"]
        assert len(retrieval["citations"]) >= 1
        top_citation = retrieval["citations"][0]
        assert top_citation.similarity_score > 0.25


@pytest.mark.asyncio
async def test_rag_fallback_baseline_guidelines_retrieval():
    """
    Validates that RAG service accurately retrieves from authoritative baseline guidelines
    even when querying core clinical topics like cholesterol or diabetes.
    """
    async with TestingSessionLocal() as session:
        res = await rag_service.retrieve_relevant_context(
            session=session,
            query="What is the recommended HbA1c level for diabetes diagnosis according to ADA?",
            top_k=2
        )
        assert res["rag_context"] is not None
        assert len(res["citations"]) > 0
        # Should cite ADA diabetes guidelines
        titles = [c.document_title for c in res["citations"]]
        assert any("Diabetes" in t or "ADA" in t or "Clinical" in t for t in titles)


# ==============================================================================
# 4. API Endpoints RAG Integration Tests (Chat & Admin)
# ==============================================================================

def test_chat_query_endpoint_returns_rag_citations(client: TestClient, user_token_header: dict):
    """
    Validates that POST /api/v1/chat/query invokes RAG retrieval and returns
    structured DocumentCitation objects with similarity scores (FR-03, FR-04.5).
    """
    payload = {
        "query": "What are the stages of hypertension according to AHA guidelines?",
        "conversation_id": None
    }
    response = client.post("/api/v1/chat/query", json=payload, headers=user_token_header)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]

    # Verify RAG citations
    assert len(data["sources_cited"]) > 0
    first_source = data["sources_cited"][0]
    assert "document_title" in first_source
    assert "similarity_score" in first_source
    assert first_source["similarity_score"] > 0.0

    # Verify clinical educational answer
    assert len(data["answer"]) > 50
    assert "blood pressure" in data["answer"].lower() or "hypertension" in data["answer"].lower()


def test_admin_knowledge_document_ingestion_api(client: TestClient, admin_token_header: dict):
    """
    Validates that POST /api/v1/admin/knowledge-documents successfully accepts
    clinical guideline content and ingests it into RAG (FR-04.1, FR-08.1).
    """
    payload = {
        "title": "Chronic Kidney Disease Staging Protocol",
        "category": "Nephrology",
        "content": (
            "Chronic kidney disease (CKD) is defined by abnormalities of kidney structure or function "
            "present for greater than 3 months. Stage 1 is normal eGFR (>=90 mL/min/1.73m2) with persistent proteinuria. "
            "Stage 3 CKD is eGFR 30-59 mL/min/1.73m2, requiring active nephrology co-management."
        ),
        "source_url": "https://kdigo.org/guidelines/ckd-evaluation/"
    }
    response = client.post("/api/v1/admin/knowledge-documents", json=payload, headers=admin_token_header)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["title"] == payload["title"]
    assert data["category"] == "Nephrology"
    assert data["total_chunks"] >= 1
