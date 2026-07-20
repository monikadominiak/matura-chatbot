from backend.rag.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

answer = pipeline.analyze_solution(
    image_path="./data/przykład4.png",   # <- tutaj swoje zdjęcie
    user_question="Czy to jest poprawne??",
)

print("\n" + "=" * 80)
print("ODPOWIEDŹ CHATBOTA")
print("=" * 80)
print(answer)