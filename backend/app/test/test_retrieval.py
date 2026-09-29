from app.query.analyzer import analyze_query
from app.retrieval.retriever import Retriever
from app.retrieval.reranker import Reranker


def main():

    query = "Flutter mein basic screen kaise create karte hain? Complete code do"

    print("\nQUERY:")
    print(query)

    # -------------------------
    # Query Analysis
    # -------------------------

    analysis = analyze_query(query)

    print("\nQUERY ANALYSIS:")
    print(analysis)

    # -------------------------
    # FAISS Retrieval
    # -------------------------

    retriever = Retriever()

    results = retriever.search(
        query,
        top_k=30,
        filters=analysis
    )

    print("\nFAISS RESULTS:", len(results))

    # -------------------------
    # Reranking
    # -------------------------

    reranker = Reranker()

    results = reranker.rerank(
        query,
        results,
        top_k=5
    )

    print("\n")
    print("=" * 70)
    print("RERANKED RESULTS")
    print("=" * 70)

    for i, result in enumerate(results, start=1):

        print(f"\nRESULT {i}")

        print(
            f"FAISS Score: "
            f"{result.get('score', 0):.4f}"
        )

        print(
            f"Rerank Score: "
            f"{result.get('rerank_score', 0):.4f}"
        )

        print(
            f"Technology: "
            f"{result.get('technology')}"
        )

        print(
            f"Framework: "
            f"{result.get('framework')}"
        )

        print(
            f"Topics: "
            f"{result.get('topics')}"
        )

        print(
            f"Source: "
            f"{result.get('source')}"
        )

        print("-" * 70)

        print(result["text"][:1200])


if __name__ == "__main__":
    main()