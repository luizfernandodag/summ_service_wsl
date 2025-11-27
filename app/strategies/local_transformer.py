from .base import SummarizationStrategy

class LocalTransformerStrategy(SummarizationStrategy):
    def summarize(self, text: str) -> str:
        return "local transformer summary"
