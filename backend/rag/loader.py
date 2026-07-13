from pathlib import Path
from langchain_core.documents import Document
from .splitter import splitter


class DataLoader:

    def __init__(self, base_path="data"):
        self.base = Path(base_path)

    def load_official(self):

        documents = []

        official = self.base / "parsed"

        for exam_folder in sorted(official.iterdir()):

            if not exam_folder.is_dir():
                continue

            exam = exam_folder.name

            for txt in sorted(exam_folder.glob("*.txt")):

                task = txt.stem

                content = txt.read_text(
                    encoding="utf8",
                    errors="ignore"
                )

                documents.append(

                    Document(

                        page_content=self.extract_task(content),

                        metadata={

                            "source": "official",

                            "exam": exam,

                            "task": task,

                            "task_text": self.extract_task(content),

                            "full_content": content

                        }

                    )

                )

        return documents

    def load_examples(self):

        documents = []

        examples = self.base / "examples"

        for topic_folder in sorted(examples.iterdir()):

            if not topic_folder.is_dir():
                continue

            topic = topic_folder.name

            for txt in sorted(topic_folder.glob("*.txt")):

                number = txt.stem

                content = txt.read_text(
                    encoding="utf8",
                    errors="ignore"
                )

                documents.append(

                    Document(

                        page_content=f"""
                        Dział matematyki:
                        {topic}

                        Treść zadania:
                        {content}
                        """,

                        metadata={

                            "source": "example",

                            "topic": topic,

                            "number": number,

                            "full_content": content

                        }

                    )

                )

        return documents

    def load_all(self):

        return self.load_official() + self.load_examples()
    def extract_task(self, text):

        if "[OFICJALNE ZASADY OCENIANIA CKE]" in text:

            text = text.split(
                "[OFICJALNE ZASADY OCENIANIA CKE]"
            )[0]

        return text


    
def split_documents(documents):
    return splitter.split_documents(documents)

if __name__ == "__main__":

    loader = DataLoader()

    official = loader.load_official()

    examples = loader.load_examples()

    print("Official:", len(official))

    print("Examples:", len(examples))

    print()

    print(official[0].metadata)

    print()

    print(official[0].page_content[:300])