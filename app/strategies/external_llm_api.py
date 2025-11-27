from .base import SummarizationStrategy

class ExternalLLMStrategy(SummarizationStrategy):
    def summarize(self, text: str) -> str:
        return "external LLM summary"
