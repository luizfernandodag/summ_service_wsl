# app/strategies/local_transformer.py
import time
from typing import Dict

# imports leves/top-level (evite imports pesados aqui)
from app.strategies.base import SummarizationStrategy
from app.core.config import settings
from app.core.logger import logger

# Flag para disponibilidade de torch/transformers (será checada em runtime)
TORCH_AVAILABLE = False

try:
    # Tenta detectar torch sem trazer tudo pro topo se não existir
    import importlib
    _torch_spec = importlib.util.find_spec("torch")
    if _torch_spec is not None:
        TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


class LocalTransformerSummarization(SummarizationStrategy):
    """
    Estratégia de sumarização usando um modelo local (e.g., T5) via Transformers.
    Faz lazy-load de torch/transformers só quando necessário.
    """

    def __init__(self):
        # Se torch não estiver disponível, explicamos claramente
        if not TORCH_AVAILABLE:
            raise RuntimeError(
                "LocalTransformerSummarization requires 'torch' (and transformers) to be installed. "
                "Set SUMMARIZATION_STRATEGY to 'external' or install torch in the container."
            )

        # Agora que sabemos que há suporte, importamos o que precisamos (lazy import)
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
            import torch  # import real agora
        except Exception as e:
            logger.exception("Falha ao importar transformers/torch durante inicialização local.")
            raise RuntimeError(f"Falha ao importar transformers/torch: {e}") from e

        self.model_name = settings.LOCAL_MODEL_NAME
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Carrega o tokenizador e o modelo
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
        except Exception as e:
            logger.exception("Erro ao carregar modelo/tokenizer local.")
            raise RuntimeError(f"Erro ao carregar modelo/tokenizer: {e}") from e

        # Cria o pipeline de sumarização (device: 0 para GPU, -1 para CPU)
        self.summarizer_pipeline = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1,
        )

        # Métricas
        self.total_inference_time_ms = 0.0
        self.total_tokens_processed = 0

    def summarize_chunk(self, text: str) -> str:
        """
        Gera um resumo para um único chunk de texto utilizando o modelo local.
        """
        start_time = time.time()

        # conta tokens de forma aproximada
        try:
            input_tokens = self.tokenizer.encode(text, return_tensors="pt", truncation=True).size(1)
        except Exception:
            input_tokens = 0

        try:
            result = self.summarizer_pipeline(
                text,
                max_length=150,
                min_length=30,
                do_sample=False,
            )

            summary = result[0].get("summary_text", "")

            # Métricas
            self.total_tokens_processed += input_tokens
            self.total_inference_time_ms += (time.time() - start_time) * 1000

            logger.info("Chunk sumariado com sucesso via modelo local.",
                        extra={"input_tokens": input_tokens, "strategy": "local"})

            return summary

        except Exception as e:
            logger.exception("Erro na sumarização local.")
            return "Erro ao gerar resumo via modelo local."

    def get_metrics(self) -> Dict[str, float]:
        return {
            "strategy": "local",
            "total_tokens_processed": self.total_tokens_processed,
            "total_inference_time_ms": self.total_inference_time_ms,
        }
