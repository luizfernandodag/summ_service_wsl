import time
from typing import Dict, Union
#from google import genai
#from google import genai

from google import genai

# from google import genai



from google.genai.errors import APIError

#from base import SummarizationStrategy
#from ..core.config import settings
#from ..core.logger import logger

from app.strategies.base import SummarizationStrategy
from app.core.config import settings
from app.core.logger import logger





class ExternalLLMSummarization(SummarizationStrategy):
    """
    Estratégia de sumarização usando um LLM externo (Google Gemini).
    """

    def __init__(self):
        # A chave de API é carregada automaticamente via settings
        self.client = genai.Client(api_key=settings.EXTERNAL_API_KEY)
        self.model_name = settings.EXTERNAL_MODEL_NAME
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.inference_time_ms = 0.0

    def summarize_chunk(self, text: str) -> str:
        """
        Gera um resumo para um único chunk de texto utilizando o LLM.
        """
        start_time = time.time()

        try:
            # O prompt define a tarefa de sumarização
            prompt = (
                "Resuma o seguinte texto de forma concisa e coerente. O resumo será "
                "posteriormente unificado com outros resumos: \n\n"
                f"TEXTO: \"{text}\""
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            # Coleta de métricas
            prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
            candidates_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
            self.total_input_tokens += prompt_tokens
            self.total_output_tokens += candidates_tokens
            # self.total_input_tokens += response.usage_metadata.prompt_token_count
            # self.total_output_tokens += response.usage_metadata.candidates_token_count

            self.inference_time_ms += (time.time() - start_time) * 1000

            logger.info("Chunk sumariado com sucesso via API externa.",
                        extra={"tokens": response.usage_metadata, "strategy": "external"})

            return response.text or ""

        except APIError as e:
            logger.error(f"Erro na API externa: {e}", extra={"strategy": "external"})
            return "Erro ao gerar resumo via API externa."
        except Exception as e:
            logger.error(f"Erro inesperado na sumarização externa: {e}", extra={"strategy": "external"})
            return "Erro inesperado."

    def get_metrics(self) -> Dict[str, Union[str, float, int]]:
        """
        Retorna as métricas de inferência.
        """
        return {
            "strategy": "external",
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "inference_time_ms": self.inference_time_ms,
            # Tempo por chunk é calculado no serviço principal, mas o total 
            # de tokens/tempo é coletado aqui.
        }