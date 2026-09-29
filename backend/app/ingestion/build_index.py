import hashlib
import json
from pathlib import Path

import numpy as np

from app.ingestion.loader import load_documents
from app.ingestion.chunker import split_into_chunks
from app.ingestion.metadata import detect_metadata

from app.embeddings.embedder import Embedder

from app.retrieval.vector_store import (
    build_and_save_index
)


def main():

    # =====================================
    # 1. Load documents
    # =====================================

    documents = load_documents(
        "knowledge_base"
    )

    # =====================================
    # 2. Chunk documents
    # =====================================

    all_chunks = []

    for document in documents:

        chunks = split_into_chunks(
            document["text"],
            chunk_size=1400,
            chunk_overlap=250
        )

        for chunk_id, chunk_text in enumerate(
            chunks
        ):

            metadata = detect_metadata(
                text=chunk_text,
                technology=document["technology"],
                source=document["source"]
            )

            all_chunks.append({

                "id": len(all_chunks),

                "chunk_id": chunk_id,

                "text": chunk_text,

                "source": document["source"],

                "filename": document["filename"],

                **metadata
            })

    print()
    print(
        f"Total chunks: {len(all_chunks)}"
    )

    if not all_chunks:

        raise RuntimeError(
            "No chunks were created. "
            "Check knowledge_base."
        )

    # =====================================
    # 3. Prepare texts
    # =====================================

    texts = [
        item["text"]
        for item in all_chunks
    ]

    # =====================================
    # 4. Checkpoint configuration
    # =====================================

    checkpoint_dir = Path(
        "vector_db/checkpoints"
    )

    checkpoint_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    batch_size = 128

    # =====================================
    # 5. Create dataset fingerprint
    # =====================================

    fingerprint = hashlib.sha256(
        json.dumps(
            texts,
            ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()

    manifest_path = (
        checkpoint_dir / "manifest.json"
    )

    manifest = {
        "fingerprint": fingerprint,
        "model": "all-MiniLM-L6-v2",
        "batch_size": batch_size,
        "normalize_embeddings": True
    }

    # =====================================
    # 6. Validate checkpoint
    # =====================================

    if manifest_path.exists():

        existing = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )

        if existing != manifest:

            raise RuntimeError(
                "\nExisting checkpoint does not "
                "match the current dataset/settings.\n\n"
                "Delete the checkpoint folder:\n"
                "rm -rf vector_db/checkpoints\n\n"
                "Then run the command again."
            )

    else:

        old_batches = list(
            checkpoint_dir.glob(
                "batch_*.npy"
            )
        )

        if old_batches:

            raise RuntimeError(
                "\nOld checkpoint files found "
                "without a manifest.\n\n"
                "Delete them:\n"
                "rm -rf vector_db/checkpoints\n\n"
                "Then run the command again."
            )

        manifest_path.write_text(
            json.dumps(
                manifest,
                indent=2
            ),
            encoding="utf-8"
        )

    # =====================================
    # 7. Load embedding model
    # =====================================

    embedder = Embedder()

    # =====================================
    # 8. Generate embeddings in batches
    # =====================================

    batch_files = []

    total = len(texts)

    print()
    print(
        "Starting embedding generation..."
    )

    print(
        f"Total texts : {total}"
    )

    print(
        f"Batch size  : {batch_size}"
    )

    print(
        "Device      : CPU"
    )

    for start in range(
        0,
        total,
        batch_size
    ):

        end = min(
            start + batch_size,
            total
        )

        batch_number = (
            start // batch_size
        )

        checkpoint = (
            checkpoint_dir
            / f"batch_{batch_number:05d}.npy"
        )

        batch_files.append(
            checkpoint
        )

        # =================================
        # Already completed
        # =================================

        if checkpoint.exists():

            print(
                f"[SKIP] Batch "
                f"{batch_number} "
                f"already completed "
                f"({end}/{total})"
            )

            continue

        # =================================
        # Generate current batch
        # =================================

        batch_texts = texts[
            start:end
        ]

        print(
            f"[EMBED] Batch "
            f"{batch_number} "
            f"({start + 1}-{end}/{total})"
        )

        batch_embeddings = (
            embedder.encode(
                batch_texts
            )
        )

        # =================================
        # Temporary file
        # =================================

        temp_file = (
            checkpoint.with_suffix(
                ".tmp"
            )
        )

        with temp_file.open(
            "wb"
        ) as file:

            np.save(
                file,
                batch_embeddings
            )

        # Atomic rename
        temp_file.replace(
            checkpoint
        )

        print(
            f"[SAVED] "
            f"{checkpoint}"
        )

    # =====================================
    # 9. Load all embeddings
    # =====================================

    print()
    print(
        "Loading embedding checkpoints..."
    )

    embeddings_list = []

    for checkpoint in batch_files:

        if not checkpoint.exists():

            raise RuntimeError(
                f"Missing checkpoint: "
                f"{checkpoint}"
            )

        embeddings_list.append(
            np.load(
                checkpoint
            )
        )

    embeddings = np.concatenate(
        embeddings_list,
        axis=0
    )

    # =====================================
    # 10. Validate embeddings
    # =====================================

    if len(embeddings) != len(
        all_chunks
    ):

        raise RuntimeError(
            "Embedding count does not "
            "match chunk count.\n"
            f"Embeddings: {len(embeddings)}\n"
            f"Chunks: {len(all_chunks)}"
        )

    print()
    print(
        f"Embeddings shape: "
        f"{embeddings.shape}"
    )

    # =====================================
    # 11. Build FAISS index
    # =====================================

    print()
    print(
        "Building FAISS index..."
    )

    build_and_save_index(
        embeddings,
        all_chunks,
        "vector_db"
    )

    print()
    print("=" * 60)
    print("INDEXING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()