import base64
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .models import TopicMatch, VisionResult

load_dotenv()


class VisionService:

    def __init__(self):

        self.client = OpenAI()

        examples_dir = Path("data/examples")

        if examples_dir.exists():
            self.available_topics = sorted(
                folder.name
                for folder in examples_dir.iterdir()
                if folder.is_dir()
            )
        else:
            self.available_topics = []

    @staticmethod
    def _encode_image(image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode("utf-8")

    @staticmethod
    def _clean_json(text: str) -> str:

        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]

        if text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    def analyze(
        self,
        image_bytes: bytes,
        question: str
    ) -> VisionResult:

        image = self._encode_image(image_bytes)

        system_prompt = f"""
Jesteś ekspertem od matury podstawowej z matematyki.

Twoim zadaniem NIE jest rozwiązywanie zadania.

Masz jedynie odczytać informacje ze zdjęcia.

Na zdjęciu może znajdować się:

- treść zadania,
- częściowe rozwiązanie ucznia,
- obliczenia,
- rysunki.

Przepisz wszystko możliwie dokładnie.

Lista dostępnych działów w bazie wiedzy:

{json.dumps(self.available_topics, ensure_ascii=False, indent=2)}

Dobierz maksymalnie 3 najlepiej pasujące działy.

Dla każdego podaj confidence od 0 do 1.

task_type wybierz spośród:

multiple_choice
equation
inequality
proof
geometry
open
other

intent wybierz spośród:

next_step
find_error
review
grade
explain

Zwróć WYŁĄCZNIE JSON.

Schemat:

{{
    "task_text":"",
    "student_solution":"",
    "student_question":"",
    "topics":[
        {{
            "name":"",
            "confidence":0.95
        }}
    ],
    "task_type":"",
    "intent":"",
    "confidence":0.99
}}
"""

        response = self.client.responses.create(

            model="gpt-5",

            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": system_prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [

                        {
                            "type": "input_text",
                            "text": question
                        },

                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image}"
                        }

                    ]
                }

            ]

        )

        output = self._clean_json(
            response.output_text
        )

        try:

            data = json.loads(output)

        except Exception as e:

            raise RuntimeError(
                f"Model zwrócił niepoprawny JSON:\n\n{response.output_text}"
            ) from e

        topics = []

        for topic in data.get("topics", []):

            try:

                topics.append(

                    TopicMatch(

                        name=topic["name"],

                        confidence=float(
                            topic["confidence"]
                        )

                    )

                )

            except Exception:
                continue

        return VisionResult(

            task_text=data.get(
                "task_text",
                ""
            ),

            student_solution=data.get(
                "student_solution",
                ""
            ),

            student_question=data.get(
                "student_question",
                question
            ),

            topics=topics,

            task_type=data.get(
                "task_type",
                "other"
            ),

            intent=data.get(
                "intent",
                "review"
            ),

            confidence=float(
                data.get(
                    "confidence",
                    0.0
                )
            )

        )