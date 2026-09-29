from app.query.analyzer import analyze_query
from app.retrieval.retriever import Retriever
from app.retrieval.reranker import Reranker
from app.llm.prompt import build_prompt


def main():

    query = "React mein component kaise create karte hain? Code example do"

    # Query analysis
    analysis = analyze_query(query)

    # Retrieval
    retriever = Retriever()

    results = retriever.search(
        query,
        top_k=30,
        filters=analysis
    )

    # Reranking
    reranker = Reranker()

    results = reranker.rerank(
        query,
        results,
        top_k=5
    )

    # Prompt
    prompt = build_prompt(
        query,
        analysis,
        results
    )

    print("\n")
    print("=" * 80)
    print("GENERATED PROMPT")
    print("=" * 80)

    print(prompt)


if __name__ == "__main__":
    main()