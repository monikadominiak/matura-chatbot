from .models import (
    VisionResult,
    SearchResult,
    PromptContext
)


class PromptBuilder:

    def build(
        self,
        vision: VisionResult,
        search: SearchResult
    ) -> PromptContext:

        official = "\n\n".join(
            d.page_content
            for d in search.official
        )

        examples = "\n\n".join(
            d.page_content
            for d in search.examples
        )

        user = f"""
Treść zadania:

{vision.task_text}

Rozwiązanie ucznia:

{vision.student_solution}

Pytanie:

{vision.student_question}
"""

        return PromptContext(

            official_context=official,

            examples_context=examples,

            user_context=user
        )