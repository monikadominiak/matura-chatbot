from rag.vision import VisionService
from pathlib import Path

vision = VisionService()
image = Path("data\przykłąd.png").read_bytes()

result = vision.analyze(
    image,
    "Co zrobiłem źle?"
)

print(result)

