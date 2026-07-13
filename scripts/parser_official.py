from pathlib import Path
import re
import json

INPUT_DIR = Path("data/official")
OUTPUT_DIR = Path("processed/official_json")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def split_tasks(text):
    pattern = r"(Zadanie\s+\d+.*?)(?=Zadanie\s+\d+|$)"
    return re.findall(pattern, text, flags=re.S)


for file in INPUT_DIR.glob("*.txt"):

    print(f"Przetwarzam {file.name}")

    text = file.read_text(
        encoding="utf8",
        errors="ignore"
    )

    exam_name = file.stem

    folder = OUTPUT_DIR / exam_name
    folder.mkdir(exist_ok=True)

    tasks = split_tasks(text)

    for task in tasks:

        nr = re.search(r"Zadanie\s+(\d+)", task)

        if nr:

            number = int(nr.group(1))

            with open(

                folder / f"task_{number:02}.json",

                "w",

                encoding="utf8"

            ) as f:

                json.dump(

                    {

                        "exam": exam_name,

                        "task_number": number,

                        "content": task

                    },

                    f,

                    indent=4,

                    ensure_ascii=False

                )

print("Gotowe.")