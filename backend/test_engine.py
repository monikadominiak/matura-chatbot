from rag.search_engine import SearchEngine

engine = SearchEngine()

query = input("Treść zadania: ")

context = engine.build_prompt_context(query)

print("\n========== OFICJALNY KLUCZ ==========\n")

print(context["official_context"])

print("\n========== PRZYKŁADY ==========\n")

print(context["examples_context"])