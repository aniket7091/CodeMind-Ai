from app.embeddings.embedder import Embedder
from app.retrieval.vector_store import load_vector_store


class Retriever:

    def __init__(
        self,
        index_path="vector_db/index.faiss",
        chunks_path="vector_db/chunks.json"
    ):

        self.index, self.chunks = load_vector_store(
            index_path,
            chunks_path
        )

        self.embedder = Embedder()

    def search(
        self,
        query,
        top_k=20,
        filters=None
    ):

        query_embedding = self.embedder.encode(
            [query]
        )

        # Get more candidates first
        scores, indices = self.index.search(
            query_embedding,
            top_k * 3
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index < 0:
                continue

            chunk = self.chunks[index].copy()

            # -------------------------
            # Metadata filtering
            # -------------------------

            if filters:

                technology = filters.get(
                    "technology"
                )

                framework = filters.get(
                    "framework"
                )

                if technology:

                    if chunk.get(
                        "technology"
                    ) != technology:
                        continue

                if framework:

                    chunk_framework = (
                        chunk.get("framework")
                        or ""
                    ).lower()

                    if framework not in chunk_framework:
                        continue

            chunk["score"] = float(score)

            results.append(chunk)

            if len(results) >= top_k:
                break

        return results