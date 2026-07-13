import base64
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """
Jesteś systemem OCR do zdjęć rozwiązań zadań maturalnych.

Twoim zadaniem NIE jest rozwiązanie zadania.
Masz jedynie przepisać tekst znajdujący się na zdjęciu.

Rozpoznaj dwie sekcje:

1. Treść zadania.
2. Rozwiązanie ucznia.

Jeżeli którejś sekcji nie ma na zdjęciu, wpisz pusty tekst.

Zwróć odpowiedź WYŁĄCZNIE w formacie JSON:

{
  "task": "...",
  "solution": "..."
}

Zasady:

- nie rozwiązuj zadania
- nie poprawiaj błędów
- nie zgaduj brakujących fragmentów
- zachowaj kolejność zapisów
- przepisz wszystkie symbole matematyczne
- zapisuj wzory jako ASCII (np. x^2, sqrt(x))
- jeśli fragment jest nieczytelny wpisz [nieczytelne]"""


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def transcribe_image(image_path: str) -> str:
    """
    Zamienia zdjęcie rozwiązania ucznia na tekst.

    Parameters
    ----------
    image_path : str

    Returns
    -------
    str
    """

    image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1500
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print(content)
        raise ValueError("OCR nie zwrócił poprawnego JSON.")

if __name__ == "__main__":
    text = transcribe_image(
        r"data/przykład4.png"
    )

    print(text)