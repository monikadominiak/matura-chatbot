from .search_engine import SearchEngine
from .solution_analyzer import SolutionAnalyzer
from .transcribe_solution import transcribe_image


class RAGPipeline:

    def __init__(self):
        self.search_engine = SearchEngine()
        self.solution_analyzer = SolutionAnalyzer()


    def analyze_solution(
        self,
        image_path: str | None,
        user_question: str,
    ):

        task_text = ""
        student_solution = ""


        
        if image_path:

            ocr = transcribe_image(
                image_path
            )

            task_text = ocr.get(
                "task",
                ""
            ).strip()

            student_solution = ocr.get(
                "solution",
                ""
            ).strip()



        if task_text:

            search_query = task_text

        elif student_solution:

            search_query = student_solution

        else:

            search_query = user_question



        print("=" * 80)
        print("TREŚĆ ZADANIA")
        print(task_text)

        print("=" * 80)
        print("ROZWIĄZANIE UCZNIA")
        print(student_solution)

        print("=" * 80)
        print("SEARCH QUERY")
        print(search_query)



        search_result = self.search_engine.search(
            search_query,
            official_k=10,
            examples_k=10,
        )


        search_result.official = [
            hit
            for hit in search_result.official
            if hit.score >= 0.55
        ]


        search_result.examples = [
            hit
            for hit in search_result.examples
            if hit.score >= 0.55
        ]



        if len(search_result.official) < 3:

            search_result.official = (
                self.search_engine.search_official(
                    search_query,
                    k=3
                )
            )



        if len(search_result.examples) < 3:

            search_result.examples = (
                self.search_engine.search_examples(
                    search_query,
                    k=3
                )
            )



       
        answer = self.solution_analyzer.analyze(

            task_text=task_text,

            student_solution=student_solution,

            user_question=user_question,

            search_result=search_result,

        )


        return answer