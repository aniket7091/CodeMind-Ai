from app.query.analyzer import analyze_query
from app.retrieval.retriever import Retriever
from app.retrieval.reranker import Reranker
from app.llm.prompt import build_prompt
from app.llm.generator import LLMGenerator


def main():

    query = "React mein component kaise create karte hain? Code example do"

    print("\nUSER QUERY")
    print("=" * 70)
    print(query)

    # -------------------------
    # 1. Query Analysis
    # -------------------------

    analysis = analyze_query(query)

    print("\nQUERY ANALYSIS")
    print("=" * 70)
    print(analysis)

    # -------------------------
    # 2. Retrieval
    # -------------------------

    retriever = Retriever()

    results = retriever.search(
        query,
        top_k=30,
        filters=analysis
    )

    print("\nFAISS RESULTS:", len(results))

    # -------------------------
    # 3. Reranking
    # -------------------------

    reranker = Reranker()

    results = reranker.rerank(
        query,
        results,
        top_k=5
    )

    print("RERANKED RESULTS:", len(results))

    # -------------------------
    # 4. Build Prompt
    # -------------------------

    prompt = build_prompt(
        query,
        analysis,
        results
    )

    # -------------------------
    # 5. Generate Answer
    # -------------------------

    generator = LLMGenerator()

    answer = generator.generate(prompt)

    print("\n")
    print("=" * 70)
    print("CODEMIND AI ANSWER")
    print("=" * 70)

    print(answer)


if __name__ == "__main__":
    main()