from fastapi import FastAPI
from app.api.routes import router


app = FastAPI(
    title="CodeMind AI",
    description="Developer-focused RAG Coding Assistant",
    version="1.0.0"
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "CodeMind AI API is running"
    }