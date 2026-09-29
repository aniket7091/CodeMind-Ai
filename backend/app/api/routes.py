from fastapi import APIRouter
from pydantic import BaseModel

from app.query.analyzer import analyze_query
from app.retrieval.retriever import Retriever
from app.retrieval.reranker import Reranker
from app.llm.prompt import build_prompt
from app.llm.generator import LLMGenerator


router = APIRouter(
    prefix="/api",
    tags=["CodeMind AI"]
)


class QueryRequest(BaseModel):
    query: str


# Initialize components
retriever = Retriever()
reranker = Reranker()
generator = LLMGenerator()


@router.post("/query")
def query_codemind(request: QueryRequest):

    query = request.query.strip()

    # Check empty query
    if not query:
        return {
            "error": "Query cannot be empty"
        }

    # 1. Analyze query
    analysis = analyze_query(query)

    # 2. Retrieve documents
    results = retriever.search(
        query,
        top_k=30,
        filters=analysis
    )

    # 3. Rerank results
    results = reranker.rerank(
        query,
        results,
        top_k=5
    )

    # 4. Build grounded prompt
    prompt = build_prompt(
        query,
        analysis,
        results
    )

    # 5. Generate answer
    answer = generator.generate(prompt)

    # 6. Remove duplicate sources
    unique_sources = []
    seen = set()

    for r in results:

        source = r.get("source")

        if source and source not in seen:

            seen.add(source)

            unique_sources.append({
                "source": source,
                "technology": r.get("technology"),
                "framework": r.get("framework")
            })

    # 7. Return response
    return {
        "answer": answer,
        "technology": analysis.get("technology"),
        "framework": analysis.get("framework"),
        "topics": analysis.get("topics"),
        "intent": analysis.get("intent"),
        "sources": unique_sources
    }