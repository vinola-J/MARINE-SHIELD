from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Analysis
from backend.schemas.ask import AskRequest, AskResponse
from rag.retriever import retrieve_relevant_chunks
from rag.generator import answer_environmental_question

router = APIRouter(tags=["Ask MARINE-SHIELD"])


@router.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask marine environmental and cleanup questions"
)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """
    Answer user marine questions grounded strictly in retrieved knowledge base documents.
    """
    search_query = request.question

    # If linked to a specific analysis, include context
    if request.analysis_id:
        record = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
        if record:
            search_query = f"{record.prediction} pollution {record.severity} severity: {request.question}"

    sources = retrieve_relevant_chunks(search_query, top_k=3)
    answer = answer_environmental_question(request.question, sources=sources)

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }
