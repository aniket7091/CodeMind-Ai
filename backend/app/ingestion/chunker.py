import re


def split_into_chunks(
    text,
    chunk_size=1400,
    chunk_overlap=250
):
    if not text.strip():
        return []

    # ---------------------------------------
    # Protect code blocks
    # ---------------------------------------

    code_blocks = []

    def protect(match):
        code_blocks.append(
            match.group(0)
        )

        return (
            f"\n__CODE_BLOCK_"
            f"{len(code_blocks) - 1}"
            f"__\n"
        )

    protected = re.sub(
        r"```[\s\S]*?```",
        protect,
        text
    )

    # ---------------------------------------
    # Split by headings
    # ---------------------------------------

    sections = re.split(
        r"(?=^#{1,6}\s+)",
        protected,
        flags=re.MULTILINE
    )

    chunks = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        paragraphs = re.split(
            r"\n\s*\n",
            section
        )

        current = ""

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            candidate = (
                f"{current}\n\n{paragraph}"
                if current
                else paragraph
            )

            if len(candidate) <= chunk_size:

                current = candidate

            else:

                if current:
                    chunks.append(
                        current.strip()
                    )

                # Large paragraph
                if len(paragraph) > chunk_size:

                    lines = paragraph.splitlines()

                    current = ""

                    for line in lines:

                        line = line.strip()

                        if not line:
                            continue

                        candidate = (
                            f"{current}\n{line}"
                            if current
                            else line
                        )

                        if len(candidate) <= chunk_size:

                            current = candidate

                        else:

                            if current:
                                chunks.append(
                                    current.strip()
                                )

                            current = line

                else:

                    current = paragraph

        if current:
            chunks.append(
                current.strip()
            )

    # ---------------------------------------
    # Restore code blocks
    # ---------------------------------------

    restored = []

    for chunk in chunks:

        for i, code in enumerate(
            code_blocks
        ):

            chunk = chunk.replace(
                f"__CODE_BLOCK_{i}__",
                code
            )

        restored.append(
            chunk
        )

    # ---------------------------------------
    # Add overlap
    # ---------------------------------------

    final_chunks = []

    for i, chunk in enumerate(restored):

        if (
            i > 0
            and chunk_overlap > 0
        ):

            previous = restored[i - 1]

            overlap = previous[
                -chunk_overlap:
            ]

            chunk = (
                overlap
                + "\n\n"
                + chunk
            )

        final_chunks.append(
            chunk.strip()
        )

    return [
        chunk
        for chunk in final_chunks
        if len(chunk) >= 80
    ]