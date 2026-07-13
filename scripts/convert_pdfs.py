import os
import fitz  # PyMuPDF
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def convert_pdf_to_txt():
    input_dir = os.path.join("data", "student_pdfs", "Dowodzenie")
    output_dir = os.path.join("data", "examples", "Dowodzenie")

    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if not file_name.endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_dir, file_name)
        print(f"🔄 Przetwarzam: {file_name}")

        doc = fitz.open(pdf_path)

        full_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # 🔥 render strony do obrazu (bez popplera)
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")

            base64_image = base64.b64encode(img_bytes).decode("utf-8")

            prompt = """
Przepisz dokładnie rozwiązanie matematyczne z obrazu do tekstu.

Zasady:
- zachowaj pełną kolejność kroków
- nie pomijaj żadnych obliczeń
- przepisuj wszystkie liczby, symbole i znaki specjalne dokładnie tak jak są na obrazie
- nie pomijaj nic co jest napisane na obrazie, nawet jeśli jest zapisane innym kolorem lub w ramce
- zwróć uwagę na to czy liczba jest dodatnia czy ujemna i przepisz dokładnie tak jak jest na obrazie
- zwróć uwagę na znaki specjalne i symbole matematyczne w tym na rodzaje zamknięcia przedziałów (okrągłe, kwadratowe, klamrowe)
- zapisuj wzory w ASCII/Unicode (np. x^2, sqrt(x))
- nie dodawaj komentarzy
- nie upraszczaj
- zwróć uwagę na to czy liczba jest ułamkiem, dziesiętnym czy całkowitym i przepisz dokładnie tak jak jest na obrazie
- zwróć uwagę na poprawną kolejność liczb w tabelkach i macierzach
- jeśli na obrazie jest tekst, który nie jest częścią rozwiązania matematycznego, przepisz go również
"""

            try:
                print(f"🧠 AI analizuje stronę {page_num + 1}...")

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1500
                )

                page_text = response.choices[0].message.content
                full_text.append(f"\n--- STRONA {page_num + 1} ---\n{page_text}")

                print(f"✅ Strona {page_num + 1} OK")

            except Exception as e:
                print(f"❌ Błąd na stronie {page_num + 1}: {e}")

        # 💾 zapis całego PDF jako jeden plik TXT
        base_name = os.path.splitext(file_name)[0]
        output_path = os.path.join(output_dir, f"{base_name}.txt")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(full_text))

        print(f"📄 Zapisano: {output_path}")


if __name__ == "__main__":
    convert_pdf_to_txt()