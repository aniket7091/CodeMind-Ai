import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class LLMGenerator:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables"
            )

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )

        self.client = Groq(
            api_key=api_key
        )

    def generate(self, prompt):

        response = self.client.chat.completions.create(
            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CodeMind AI, a developer-focused "
                        "RAG coding assistant. Follow the instructions "
                        "provided in the user prompt strictly."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            max_tokens=3000
        )

        return response.choices[0].message.content