from pathlib import Path


def load_documents(knowledge_base_dir="knowledge_base"):
    root = Path(knowledge_base_dir)

    if not root.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: {root.resolve()}"
        )

    documents = []

    for path in sorted(root.rglob("*.txt")):

        # Combined corpus ko dobara load nahi karna
        if path.name == "all_documents.txt":
            continue

        try:
            text = path.read_text(
                encoding="utf-8"
            ).strip()
        except UnicodeDecodeError:
            text = path.read_text(
                encoding="utf-8",
                errors="ignore"
            ).strip()

        if len(text) < 100:
            continue

        relative = path.relative_to(root)

        # knowledge_base/nodejs/file.txt
        # relative.parts = ("nodejs", "file.txt")
        parts = relative.parts

        technology = (
            parts[0]
            if len(parts) > 1
            else "unknown"
        )

        documents.append({
            "text": text,
            "source": str(path),
            "technology": technology,
            "filename": path.name
        })

    print(
        f"Loaded documents: {len(documents)}"
    )

    return documents