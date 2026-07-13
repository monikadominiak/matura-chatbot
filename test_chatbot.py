from backend.rag.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

answer = pipeline.analyze_solution(
    image_path="./data/przykład3.png",   # <- tutaj swoje zdjęcie
    user_question="Czy można tak zapisać to rozwiązanie?"
)

print("\n" + "=" * 80)
print("ODPOWIEDŹ CHATBOTA")
print("=" * 80)
print(answer)