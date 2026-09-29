from pathlib import Path
import json

import faiss
import numpy as np


VECTOR_DB_DIR = Path("vector_db")


def build_and_save_index(
    embeddings,
    chunks,
    output_dir="vector_db"
):
    """
    Create FAISS index and save it along with
    chunk metadata.
    """

    output = Path(output_dir)

    output.mkdir(
        parents=True,
        exist_ok=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2D array."
        )

    if len(embeddings) == 0:
        raise ValueError(
            "No embeddings received."
        )

    dimension = embeddings.shape[1]

    # Embeddings are normalized,
    # so Inner Product works as cosine similarity.
    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    # -----------------------------
    # Save FAISS index
    # -----------------------------

    index_path = (
        output / "index.faiss"
    )

    faiss.write_index(
        index,
        str(index_path)
    )

    # -----------------------------
    # Save chunks + metadata
    # -----------------------------

    chunks_path = (
        output / "chunks.json"
    )

    with chunks_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("VECTOR STORE CREATED")
    print("=" * 60)

    print(
        f"Vectors   : {index.ntotal}"
    )

    print(
        f"Dimension : {dimension}"
    )

    print(
        f"Index     : {index_path}"
    )

    print(
        f"Chunks    : {chunks_path}"
    )


def load_vector_store(
    index_path="vector_db/index.faiss",
    chunks_path="vector_db/chunks.json"
):
    """
    Load FAISS index and chunk metadata.
    """

    if not Path(index_path).exists():
        raise FileNotFoundError(
            f"FAISS index not found: {index_path}"
        )

    if not Path(chunks_path).exists():
        raise FileNotFoundError(
            f"Chunks file not found: {chunks_path}"
        )

    index = faiss.read_index(
        index_path
    )

    with open(
        chunks_path,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    return index, chunks