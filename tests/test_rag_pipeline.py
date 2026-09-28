import pytest
from rag.retriever import retrieve_relevant_chunks, retrieve_for_pollution_analysis, is_vectorstore_available
from rag.generator import generate_pollution_assessment, answer_environmental_question


def test_vectorstore_available():
    assert is_vectorstore_available() is True


def test_retrieve_relevant_chunks():
    chunks = retrieve_relevant_chunks("plastic microplastic marine pollution", top_k=3)
    assert len(chunks) > 0
    first = chunks[0]
    assert "document_name" in first
    assert "chunk" in first
    assert "similarity_score" in first
    assert first["similarity_score"] > 0.0


def test_generate_pollution_assessment_structure():
    sources = retrieve_for_pollution_analysis("Plastic Waste", "MEDIUM")
    ai_assessment, rec = generate_pollution_assessment(
        prediction="Plastic Waste",
        confidence=0.87,
        severity="MEDIUM",
        severity_score=0.62,
        severity_reason="Scattered plastic debris along tidal boundary.",
        sources=sources
    )

    assert "### 1. Detection Explanation" in ai_assessment
    assert "### 2. Environmental Significance" in ai_assessment
    assert "### 4. Monitoring Considerations" in ai_assessment
    assert "### 5. Limitations" in ai_assessment
    assert "Actionable Field Response" in rec or "Response" in rec


def test_answer_environmental_question():
    sources = retrieve_relevant_chunks("ghost net entanglement fauna", top_k=2)
    ans = answer_environmental_question("Why are ghost nets dangerous?", sources)
    assert len(ans) > 20
