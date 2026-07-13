from dataclasses import dataclass
from typing import List

from langchain_core.documents import Document


# ----------------------------
# Vision
# ----------------------------

@dataclass
class VisionResult:

    task_text: str

    student_solution: str

    student_question: str

    task_type: str

    intent: str

    confidence: float


# ----------------------------
# Retrieval
# ----------------------------

@dataclass
class SearchHit:

    document: Document

    score: float


@dataclass
class SearchResult:

    official: List[SearchHit]

    examples: List[SearchHit]


# ----------------------------
# Prompt
# ----------------------------

@dataclass
class PromptContext:

    official_context: str

    examples_context: str

    user_context: str


# ----------------------------
# Chat
# ----------------------------

@dataclass
class ChatRequest:

    image_bytes: bytes

    question: str


@dataclass
class ChatResponse:

    answer: str

    confidence: float

    official_exam: str | None

    official_task: str | None