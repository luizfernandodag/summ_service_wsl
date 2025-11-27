from abc import ABC, abstractmethod
from typing import List


class SummarizationStrategy(ABC):
    """
    Interface (Classe Abstrata) para definir o contrato de todas as estratégias de sumarização.
    Garante que 'local' e 'external' tenham o mesmo método 'summarize_chunk'.
    """

    @abstractmethod
    def summarize_chunk(self, text: str) -> str:
        """
        Método para sumarizar um único chunk de texto.

        Args:
            text: O chunk de texto a ser resumido.

        Returns:
            O resumo do chunk.
        """
        raise NotImplementedError

    @abstractmethod
    def get_metrics(self) -> dict:
        """
        Método para coletar métricas específicas da inferência (tokens, tempo, etc.).
        """
        raise NotImplementedError