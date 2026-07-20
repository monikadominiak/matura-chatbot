# import base64
# import os
# import json
# from dotenv import load_dotenv
# from openai import OpenAI

# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# PROMPT = """
# Jesteś systemem OCR do zdjęć rozwiązań zadań maturalnych.

# Twoim zadaniem NIE jest rozwiązanie zadania.
# Masz jedynie przepisać tekst znajdujący się na zdjęciu.

# Rozpoznaj dwie sekcje:

# 1. Treść zadania.
# 2. Rozwiązanie ucznia.

# Jeżeli którejś sekcji nie ma na zdjęciu, wpisz pusty tekst.

# Zwróć odpowiedź WYŁĄCZNIE w formacie JSON:

# {
#   "task": "...",
#   "solution": "..."
# }

# Zasady:

# - nie rozwiązuj zadania
# - nie poprawiaj błędów
# - nie zgaduj brakujących fragmentów
# - zachowaj kolejność zapisów
# - przepisz wszystkie symbole matematyczne
# - zapisuj wzory jako ASCII (np. x^2, sqrt(x))
# - jeśli fragment jest nieczytelny wpisz [nieczytelne]"""


# def encode_image(image_path: str) -> str:
#     with open(image_path, "rb") as f:
#         return base64.b64encode(f.read()).decode("utf-8")


# def transcribe_image(image_path: str) -> str:
#     """
#     Zamienia zdjęcie rozwiązania ucznia na tekst.

#     Parameters
#     ----------
#     image_path : str

#     Returns
#     -------
#     str
#     """

#     image = encode_image(image_path)

#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": PROMPT
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/png;base64,{image}"
#                         }
#                     }
#                 ]
#             }
#         ],
#         max_tokens=4000
#     )

#     content = response.choices[0].message.content.strip()

#     try:
#         return json.loads(content)
#     except json.JSONDecodeError:
#         print(content)
#         raise ValueError("OCR nie zwrócił poprawnego JSON.")

# if __name__ == "__main__":
#     text = transcribe_image(
#         r"data/przykład4.png"
#     )

#     print(text)

import base64
import os
import json
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageOps, ImageEnhance

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """
Przepisz dokładnie cały tekst widoczny na zdjęciu — treść zadania i rozwiązanie ucznia.
Nie rozwiązuj zadania, nie poprawiaj błędów, nie zgaduj nieczytelnych fragmentów.
Zachowaj układ i kolejność linii z oryginału.
Wzory zapisuj jako ASCII (np. x^2, sqrt(x)).
Jeśli fragment jest nieczytelny, wpisz [nieczytelne].
Jeśli linia jest przekreślona, wpisz [przekreślone: ...] i przepisz to, co da się odczytać, lub samo [przekreślone] jeśli nic się nie da odczytać.
Przykład błędu, którego NIE wolno popełnić:
Jeśli na zdjęciu widać niewyraźny zapis "2 sin x · [?] − cos 4x = 0", 
NIE WOLNO zamieniać go na inne, logicznie pasujące równanie typu "sin(pi/4-2x)=0".
Zamiast tego napisz: "2 sin x · [nieczytelne] − cos 4x = 0" lub całą linię jako [nieczytelne].
Zwróć odpowiedź WYŁĄCZNIE w formacie JSON:

{
  "task": "...",
  "solution": "..."
}

"""


def preprocess_image(image_path: str, max_dimension: int = 2048) -> str:
    """
    Poprawia jakość zdjęcia przed wysłaniem do OCR:
    - koryguje orientację (EXIF)
    - konwertuje do skali szarości + zwiększa kontrast
    - skaluje w górę, jeśli obraz jest za mały

    Returns
    -------
    str
        Obraz zakodowany w base64 (PNG).
    """
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)

    img = ImageOps.grayscale(img)
    img = ImageEnhance.Contrast(img).enhance(1.5)

    if max(img.size) < max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def transcribe_image(image_path: str) -> dict:
    """
    Zamienia zdjęcie rozwiązania ucznia na tekst.

    Parameters
    ----------
    image_path : str

    Returns
    -------
    dict
    """

    image = preprocess_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0,
        response_format={"type": "json_object"},
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
                            "url": f"data:image/png;base64,{image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=4000
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print(content)
        raise ValueError("OCR nie zwrócił poprawnego JSON.")


if __name__ == "__main__":
    text = transcribe_image(
        r"data/przykłąd.png"
    )

    print(text)