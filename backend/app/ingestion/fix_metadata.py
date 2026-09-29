import json
import shutil
from pathlib import Path
from collections import Counter

import faiss

from app.ingestion.metadata import detect_metadata


CHUNKS_PATH = Path("vector_db/chunks.json")
BACKUP_PATH = Path(
    "vector_db/chunks_backup_before_metadata_fix.json"
)
INDEX_PATH = Path("vector_db/index.faiss")


def main():

    print("Loading chunks...")

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Chunks loaded: {len(chunks)}")

    # Backup
    shutil.copy2(CHUNKS_PATH, BACKUP_PATH)

    print(f"Backup created: {BACKUP_PATH}")

    # Fix metadata without changing chunk order/text
    for chunk in chunks:

        metadata = detect_metadata(
            text=chunk["text"],
            technology=chunk["technology"],
            source=chunk["source"],
        )

        chunk.update(metadata)

    # Save
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(
            chunks,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\nMetadata updated successfully.")

    # -------------------------
    # Validate FAISS alignment
    # -------------------------

    index = faiss.read_index(str(INDEX_PATH))

    print("\nVALIDATION")
    print("=" * 50)

    print("FAISS vectors :", index.ntotal)
    print("JSON chunks   :", len(chunks))

    if index.ntotal == len(chunks):
        print("✅ FAISS and chunks.json are aligned")
    else:
        print("❌ MISMATCH!")
        return

    # -------------------------
    # Framework statistics
    # -------------------------

    framework_counts = Counter(
        chunk["framework"]
        for chunk in chunks
    )

    technology_counts = Counter(
        chunk["technology"]
        for chunk in chunks
    )

    print("\nTECHNOLOGY COUNTS")
    print("=" * 50)

    for tech, count in technology_counts.most_common():
        print(f"{tech:15} : {count}")

    print("\nFRAMEWORK COUNTS")
    print("=" * 50)

    for framework, count in framework_counts.most_common():
        print(f"{framework:20} : {count}")

    # -------------------------
    # Express validation
    # -------------------------

    express_chunks = [
        chunk
        for chunk in chunks
        if chunk["framework"] == "express"
    ]

    print("\nEXPRESS CHUNKS")
    print("=" * 50)

    print("Express chunks:", len(express_chunks))

    for chunk in express_chunks[:5]:

        print("\nSource:", chunk["source"])
        print("Technology:", chunk["technology"])
        print("Framework:", chunk["framework"])
        print("Language:", chunk["language"])
        print("Topics:", chunk["topics"])


if __name__ == "__main__":
    main()