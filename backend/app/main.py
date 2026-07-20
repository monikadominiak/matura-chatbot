import os
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend.rag.rag_pipeline import RAGPipeline

app = FastAPI(title="Matura Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RAGPipeline()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"message": "Matura Chatbot API działa"}


@app.post("/analyze")
async def analyze(
    question: str = Form(...),
    image: UploadFile | None = File(None),
):

    image_path = None

    try:

        if image:

            image_path = UPLOAD_DIR / image.filename

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(
                    image.file,
                    buffer
                )


        result = pipeline.analyze_solution(
            image_path=str(image_path) if image_path else None,
            user_question=question,
        )

        return {
            "answer": result
        }


    finally:

        if image_path and image_path.exists():
            os.remove(image_path)