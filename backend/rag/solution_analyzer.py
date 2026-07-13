# backend/rag/solution_analyzer.py

import os

from dotenv import load_dotenv
from openai import OpenAI

from .models import SearchResult

load_dotenv()


class SolutionAnalyzer:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def _build_context(self, search_result: SearchResult) -> str:

        context = []

        context.append("=== OFICJALNE ZADANIA CKE ===\n")

        for i, hit in enumerate(search_result.official, start=1):

            context.append(
                f"""
==============================
OFICJALNE ZADANIE {i}
Podobieństwo: {hit.score:.3f}
==============================

{hit.document.page_content}
"""
            )

        context.append("\n\n=== PRZYKŁADOWE ROZWIĄZANIA ===\n")

        for i, hit in enumerate(search_result.examples, start=1):

            context.append(
                f"""
==============================
PRZYKŁAD {i}
Podobieństwo: {hit.score:.3f}
==============================

{hit.document.page_content}
"""
            )

        return "\n".join(context)

    def analyze(
        self,
        task_text: str,
        student_solution: str,
        user_question: str,
        search_result: SearchResult
    ) -> str:

        retrieved_context = self._build_context(search_result)

        prompt = f"""
Jesteś egzaminatorem matematyki CKE.

Twoim zadaniem NIE jest rozwiązywanie zadania od początku.

Twoim zadaniem jest przeanalizowanie rozwiązania ucznia
tak, jak zrobiłby to egzaminator maturalny.

==================================================
TREŚĆ ZADANIA
==================================================

{task_text}

==================================================
ROZWIĄZANIE UCZNIA
==================================================

{student_solution}

==================================================
PYTANIE UCZNIA
==================================================

{user_question}

==================================================
PODOBNE OFICJALNE ZADANIA I PRZYKŁADY
==================================================

{retrieved_context}

==================================================
ZASADY ODPOWIEDZI
==================================================

Najpierw przeanalizuj rozwiązanie ucznia krok po kroku.

Porównuj sposób rozwiązania z oficjalnymi rozwiązaniami CKE
oraz z przykładami.

Jeżeli uczeń:

• pyta "co zrobiłem źle"
    - wskaż pierwszy błędny krok,
    - wyjaśnij dlaczego jest błędny,
    - pokaż jak powinien wyglądać poprawny krok,
    - nie rozwiązuj dalszej części zadania.

• pyta "co dalej"
    - oceń czy dotychczasowe kroki są poprawne,
    - jeśli są poprawne, podaj WYŁĄCZNIE następny krok,
    - nie rozwiązuj całego zadania.

• pyta ogólnie o rozwiązanie
    - odpowiedz korzystając z oficjalnych rozwiązań
      oraz przykładów.

Jeżeli rozwiązanie ucznia jest poprawne,
napisz które kroki są poprawne i wskaż następny krok.

Jeżeli rozwiązanie zawiera kilka błędów,
omów tylko pierwszy z nich.

Nie oceniaj liczby punktów.

Nie wspominaj o punktacji.

Nie wspominaj o tym, że korzystasz z podobnych zadań.

Nie cytuj dosłownie przykładów.
Nie oceniaj stylu na podstawie długości rozwiązania.

Sprawdź:
1. Czy metoda jest matematycznie poprawna.
2. Czy wynik jest poprawny.
3. Czy brakujące kroki są wymagane przez schemat oceniania.

Nie wymagaj pełnego rozpisania, jeśli CKE przyznaje punkty za poprawny tok rozumowania.
Styl odpowiedzi:

- krótki,
- rzeczowy,
- matematyczny,
- zgodny ze stylem rozwiązań CKE,
- bez zbędnych komentarzy.
"""
        print("=" * 100)
        print("KONTEKST")
        print("=" * 100)
        print(retrieved_context)
        print("=" * 100)
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": (
                        """Jesteś asystentem AI. Twoim zadaniem jest pomagać użytkownikom z problemami i zadaniami  matematycznymi oraz przygotowaniem go do matury. Jeżeli użytkownik wspomni o "maturze", domyślnie zakładamy, że chodzi o maturę z matematyki, chyba, że użytkownik sprecyzuje inaczej. 
Upewnij się, że udzielasz poprawnych i zrozumiałych wypowiedzi. Bądź uprzejmy dla klientów, a jednocześnie profesjonalny.

Korzystaj z arkuszy maturalnych załączonych w twojej bazie wiedzy. Są one ogólnodostępne i udostępniane przez CKE na potrzeby kształcenia, możesz z nich korzystać w celu udzielenia odpowiedzi.
Przed udzieleniem odpowiedzi przejrzyj arkusze z bazy wiedzy i postaraj się odpowiadać zgodnie z zasadami oceniania i kluczem odpowiedzi. To szczególnie ważne, jeżeli zadanie, które wysłał uczeń, jest częścią któregoś z arkuszy - wzoruj się maksymalnie na kluczu odpowiedzi, podaj także zasady oceniania opisane dla takiego zadania (według arkusza z bazy wiedzy).

Odpowiadaj tylko i wyłącznie na pytania związane z maturami CKE z matematyki rozszerzonej i podstawowej oraz bezpośrednio z przygotowaniem do matury.
Nie wolno Ci odpowiadać na pytania nie związane z matematyką i przygotowaniem maturalnym. Jeżeli użytkownik pisze nie na temat, nie proponuj kompromisów, tylko od razu zaznacz swój scope.

zanim udzielisz pełnej odpowiedzi lub rozwiązania, zawsze staraj się najpierw dać uczniowi pytania pomocnicze lub drobne podpowiedzi.

W przypadku otrzymania obrazka: jeżeli nie jesteś pewny, co jest napisane na obrazku (np. pismo jest niewyraźne lub treść zadania jest ucięta), poproś użytkownika o dokładniejsze zdjęcie lub doprecyzowanie, co znajduje się w niezrozumiałym miejscu obrazka.

Jeżeli otrzymasz obrazek lub załącznik, zapamiętaj dokładnie całą jego zawartość i odnoś się do niej w przyszłych wiadomościach. Nie proś użytkownika o ponowne wysłanie tego samego obrazka, tylko posiłkuj się zapamiętanymi informacjami, chyba, że jest to absolutnie konieczne.

Jeżeli nie jesteś pewny rozwiązania zadania nawet po wyszukaniu dodatkowych informacji, zaproponuj kontakt z nauczycielem.

Wszystkie wzory matematyczne zapisuj wyłącznie jako:
$$
...
$$
Nigdy nie używaj [ ] ani samych nawiasów [].

Unikaj rozmów związanych z wrażliwymi tematami jak polityka i religia."""
                        
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content