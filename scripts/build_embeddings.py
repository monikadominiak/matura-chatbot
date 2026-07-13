from pathlib import Path
import json

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.rag.loader import DataLoader


load_dotenv()


# ============================
# USTAWIENIA
# ============================

VECTOR_DB = Path("embeddings_test")

DESCRIPTION_FILE = Path("descriptions.json")


# TEST
# ustaw None żeby zrobić całość

MAX_OFFICIAL = None
MAX_EXAMPLES = None



# ============================
# LLM
# ============================


llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)



# ============================
# CACHE OPISÓW
# ============================


def load_descriptions():

    if DESCRIPTION_FILE.exists():

        with open(
            DESCRIPTION_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)


    return {}



def save_descriptions(data):

    with open(
        DESCRIPTION_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )



# ============================
# GENEROWANIE OPISU
# ============================


def create_description(text):


    prompt = f"""
Jesteś ekspertem od matematyki na poziomie matury.

Przeanalizuj poniższe zadanie i przygotuj opis
do wyszukiwania podobnych zadań matematycznych.

Nie rozwiązuj zadania.

Dwa zadania są podobne wtedy,
gdy można je rozwiązać tą samą metodą.

Skup się na:

- strukturze matematycznej problemu,
- metodzie rozwiązania,
- użytych wzorach,
- twierdzeniach,
- zależnościach matematycznych.


Uwzględnij:

1. Główny dział matematyki

2. Używane pojęcia

3. Typ problemu

4. Co trzeba znaleźć lub zrobić

5. Potrzebne twierdzenia/metody

6. Najważniejszy wzorzec matematyczny
(np.
delta,
twierdzenie Pitagorasa,
podobieństwo trójkątów,
wzór ciągu geometrycznego,
własności logarytmów)


7. Słowa kluczowe opisujące metodę rozwiązania.


Nie skupiaj się na:
- konkretnych liczbach,
- nazwach arkuszy,
- numerach zadań.


Treść zadania:

{text}


Opis matematyczny:
"""


    response = llm.invoke(prompt)


    return response.content



# ============================
# PRZYGOTOWANIE DOKUMENTÓW
# ============================


def prepare_documents(
        documents,
        cache
):

    result = []


    for i, doc in enumerate(documents):


        # unikalny identyfikator

        key = (
            doc.metadata.get("exam","")
            + "_"
            +
            doc.metadata.get("task","")
        )


        if key in cache:


            print(
                f"[CACHE] {i+1}/{len(documents)}"
            )


            description = cache[key]


        else:


            print(
                f"[GPT] Opisuję {i+1}/{len(documents)}"
            )


            description = create_description(
                doc.page_content
            )


            cache[key] = description


            save_descriptions(
                cache
            )



        combined_text = f"""
TREŚĆ ZADANIA
====================

{doc.page_content}


OPIS MATEMATYCZNY
====================

{description}
"""

        metadata = dict(doc.metadata)
        metadata["description"] = description
        result.append(

            Document(

                page_content=combined_text,


                metadata=metadata

                    

            )

        )


    return result



# ============================
# WCZYTANIE
# ============================


loader = DataLoader()


official = loader.load_official()

examples = loader.load_examples()



if MAX_OFFICIAL:

    official = official[:MAX_OFFICIAL]


if MAX_EXAMPLES:

    examples = examples[:MAX_EXAMPLES]



print(
    "Official:",
    len(official)
)

print(
    "Examples:",
    len(examples)
)



# ============================
# CACHE
# ============================


description_cache = load_descriptions()



print(
    "Opisów w cache:",
    len(description_cache)
)



# ============================
# GENEROWANIE
# ============================


print("\nOFFICIAL")

official = prepare_documents(
    official,
    description_cache
)



print("\nEXAMPLES")

examples = prepare_documents(
    examples,
    description_cache
)



# ============================
# EMBEDDINGI
# ============================


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)



# ============================
# CHROMA
# ============================


import time

BATCH_SIZE = 50


def build_database(documents, directory, collection_name):
    db = Chroma(
        persist_directory=str(directory),
        embedding_function=embeddings,
        collection_name=collection_name,
    )

    total = len(documents)

    for i in range(0, total, BATCH_SIZE):

        batch = documents[i:i + BATCH_SIZE]

        while True:
            try:
                db.add_documents(batch)

                print(
                    f"{collection_name}: {min(i+BATCH_SIZE,total)}/{total}"
                )

                break

            except Exception as e:

                if "rate_limit" in str(e).lower():

                    print("Rate limit - czekam 10 sekund...")

                    time.sleep(10)

                else:
                    raise

        time.sleep(2)

print("\nTworzenie bazy official")

build_database(
    official,
    VECTOR_DB / "official",
    "official"
)

print("\nTworzenie bazy examples")

build_database(
    examples,
    VECTOR_DB / "examples",
    "examples"
)

print("\nGotowe!")