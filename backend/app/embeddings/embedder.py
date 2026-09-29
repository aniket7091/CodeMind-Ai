import gc

import numpy as np

from sentence_transformers import (
    SentenceTransformer
)


MODEL_NAME = "all-MiniLM-L6-v2"


class Embedder:

    def __init__(
        self,
        model_name=MODEL_NAME
    ):

        print(
            f"Loading embedding model: "
            f"{model_name}"
        )

        # IMPORTANT:
        # Use CPU to avoid MPS memory crash.
        self.model = SentenceTransformer(
            model_name,
            device="cpu"
        )

        print(
            "Device: CPU"
        )

    def encode(
        self,
        texts
    ):

        embeddings = []

        batch_size = 8

        total = len(texts)

        for start in range(
            0,
            total,
            batch_size
        ):

            end = min(
                start + batch_size,
                total
            )

            batch = texts[
                start:end
            ]

            result = self.model.encode(
                batch,
                batch_size=batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False
            )

            embeddings.append(
                result
            )

            if (
                start == 0
                or end % 400 == 0
                or end == total
            ):

                print(
                    f"Embedded: "
                    f"{end}/{total}"
                )

        result = np.vstack(
            embeddings
        ).astype(
            "float32"
        )

        gc.collect()

        return result