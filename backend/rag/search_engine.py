from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .models import SearchHit, SearchResult
from .description_generator import DescriptionGenerator



class SearchEngine:


    def __init__(self):

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )


        self.official = Chroma(

            persist_directory="embeddings_test/official",

            embedding_function=embeddings,

            collection_name="official"

        )


        self.examples = Chroma(

            persist_directory="embeddings_test/examples",

            embedding_function=embeddings,

            collection_name="examples"

        )



        self.description_generator = (
            DescriptionGenerator()
        )



    def _search(
        self,
        db: Chroma,
        query: str,
        k: int
    ):


        results = db.similarity_search_with_score(

            query,

            k=k

        )


        hits = []


        for document, distance in results:


            score = 1 / (1 + distance)





            if "full_content" in document.metadata:


                document.page_content = (
                    document.metadata["full_content"]
                )


            hits.append(

                SearchHit(

                    document=document,

                    score=score

                )

            )


        return hits



    def search_official(
        self,
        query: str,
        k: int = 5
    ):


        return self._search(

            self.official,

            query,

            k

        )



    def search_examples(
        self,
        query: str,
        k: int = 5
    ):


        return self._search(

            self.examples,

            query,

            k

        )



    def search(
        self,
        query: str,
        official_k: int = 10,
        examples_k: int = 10
    ):


        

        description = (
            self.description_generator.generate(
                query
            )
        )


        print("\nOpis zapytania:")
        print(description)



        official = self.search_official(

            description,

            official_k

        )


        examples = self.search_examples(

            description,

            examples_k

        )


        return SearchResult(

            official=official,

            examples=examples

        )