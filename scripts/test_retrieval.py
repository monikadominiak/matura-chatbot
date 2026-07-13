from dotenv import load_dotenv

load_dotenv()

from backend.rag.search_engine import SearchEngine

engine = SearchEngine()

while True:

    print("\nWklej treść zadania (ENTER dwa razy aby zakończyć):")

    lines = []

    while True:
        line = input()

        if line == "":
            break

        lines.append(line)

    query = "\n".join(lines)

    if query.lower() == "exit":
        break

    results = engine.search(
        query,
        official_k=5,
        examples_k=5
    )
    print("\nNajbardziej podobne zadania:\n")

    print("\n=== OFICJALNE ===")

    for i, hit in enumerate(results.official, start=1):

        print("=" * 80)
        print(f"{i}. score = {hit.score:.4f}")
        print(hit.document.metadata)
        print()
        print(hit.document.page_content[:700])


    print("\n=== PRZYKŁADY ===")

    for i, hit in enumerate(results.examples, start=1):

        print("=" * 80)
        print(f"{i}. score = {hit.score:.4f}")
        print(hit.document.metadata)
        print()
        print(hit.document.page_content[:700])