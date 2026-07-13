from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

VECTOR_DB = Path("vector_db")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

official_db = Chroma(
    persist_directory=str(VECTOR_DB / "official"),
    embedding_function=embeddings,
    collection_name="official"
)

example_db = Chroma(
    persist_directory=str(VECTOR_DB / "examples"),
    embedding_function=embeddings,
    collection_name="examples"
)

official_retriever = official_db.as_retriever(
    search_kwargs={"k": 3}
)

example_retriever = example_db.as_retriever(
    search_kwargs={"k": 3}
)

while True:

    query = input("\nZapytanie: ")

    if query.lower() == "exit":
        break

    print("\n=== OFICJALNE ZADANIA ===")

    docs = official_retriever.invoke(query)

    for i, doc in enumerate(docs, 1):

        print(f"\n{i}. {doc.metadata}")
        print(doc.page_content[:300])
        print("-" * 60)

    print("\n=== PRZYKŁADY ===")

    docs = example_retriever.invoke(query)

    for i, doc in enumerate(docs, 1):

        print(f"\n{i}. {doc.metadata}")
        print(doc.page_content[:300])
        print("-" * 60)