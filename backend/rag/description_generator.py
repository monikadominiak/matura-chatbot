from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class DescriptionGenerator:

    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0
        )


    def generate(self, task_text: str):

        prompt = ChatPromptTemplate.from_template(
"""
Przeanalizuj zadanie matematyczne.

Nie rozwiązuj go.

Stwórz krótki opis zawierający:

- dział matematyki
- używane pojęcia
- typ zadania
- co tzreba rozwiązać/znależć/zrobić

Nie używaj konkretnych liczb z zadania.

Zadanie:

{task}

Opis:
"""
        )


        chain = prompt | self.llm


        response = chain.invoke(
            {
                "task": task_text
            }
        )


        return response.content