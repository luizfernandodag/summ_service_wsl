from abc import ABC, abstractmethod

class SummarizationStrategy(ABC):

    @abstractmethod
    def summarize(self, text: str) -> str:
        pass
