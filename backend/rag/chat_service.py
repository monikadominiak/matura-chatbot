from .vision import VisionService
from .search_engine import SearchEngine
from .prompt_builder import PromptBuilder


class ChatService:

    def __init__(self):

        self.vision = VisionService()

        self.search = SearchEngine()

        self.builder = PromptBuilder()