import time
import anyio
from typing import Dict, List, Type
from ..core.config import settings
from ..core.logger import logger
from ..services.text_processor import TextProcessor
from ..strategies.base import SummarizationStrategy
from ..strategies.local_transformer import LocalTransformerSummarization
from ..strategies.external_llm_api import ExternalLLMSummarization


class SummarizationService:
    """
    Serviço principal que orquestra a sumarização, 
    escolhendo a estratégia e gerenciando o processamento paralelo.
    """

    def __init__(self):
        self.processor = TextProcessor()
        self.strategy: SummarizationStrategy = self._load_strategy()
        self.metrics = {}

    def _load_strategy(self) -> SummarizationStrategy:
        """
        Carrega a estratégia de sumarização baseada na variável de ambiente.
        """
        strategy_map: Dict[str, Type[SummarizationStrategy]] = {
            "local": LocalTransformerSummarization,
            "external": ExternalLLMSummarization,
        }

        strategy_name = settings.SUMMARIZATION_STRATEGY.lower()

        if strategy_name not in strategy_map:
            logger.error(f"Estratégia inválida: {strategy_name}. Usando 'local' como fallback.")
            strategy_name = "local"

        logger.info(f"Estratégia de sumarização selecionada: {strategy_name}")
        return strategy_map[strategy_name]()

    async def _process_chunk_async(self, chunk: str, chunk_index: int, results: List):
        """
        Executa a sumarização de um chunk de forma assíncrona/concorrente.
        """
        start_time = time.time()

        # Chama o método síncrono da estratégia, 
        # que será executado em um thread pool (AnyIO/Starlette)
        summary = await anyio.to_thread.run_sync(
            self.strategy.summarize_chunk,
            chunk
        )

        time_per_chunk = (time.time() - start_time) * 1000  # em ms

        logger.info("Chunk processado.",
                    extra={"chunk_index": chunk_index, "time_ms": f"{time_per_chunk:.2f}"})

        # Adiciona o resultado à lista compartilhada
        results.append({
            "index": chunk_index,
            "summary": summary,
            "time_per_chunk_ms": time_per_chunk
        })

    async def summarize(self, text: str) -> Dict:
        """
        Fluxo principal de sumarização, com chunking e execução paralela.
        """
        full_process_start_time = time.time()

        # 1. Dividir em Chunks
        chunks = self.processor.split_into_chunks(text)

        if not chunks:
            return {"summary": "O texto de entrada está vazio.", "metrics": {}}

        # 2. Processamento Paralelo/Assíncrono
        # Usamos um Nursery do AnyIO para gerenciar as tarefas concorrentes
        chunk_results = []
        async with anyio.create_task_group() as tg:
            for i, chunk in enumerate(chunks):
                tg.start_soon(self._process_chunk_async, chunk, i, chunk_results)

        # Ordenar os resultados para garantir que o resumo final esteja na ordem correta
        chunk_results.sort(key=lambda x: x["index"])
        summaries = [r["summary"] for r in chunk_results]

        # 3. Unificação
        final_summary = self.processor.unify_summaries(summaries)

        full_process_end_time = time.time()

        # 4. Coleta de Métricas
        self.metrics = self._generate_final_metrics(chunk_results, full_process_start_time, full_process_end_time)

        return {
            "summary": final_summary,
            "metrics": self.metrics
        }

    def _generate_final_metrics(self, chunk_results: List[Dict], start_time: float, end_time: float) -> Dict:
        """
        Calcula e consolida todas as métricas exigidas.
        """
        # Métricas globais
        total_inference_time_ms = (end_time - start_time) * 1000
        total_chunk_time_ms = sum(r["time_per_chunk_ms"] for r in chunk_results)

        # Métricas específicas da estratégia (tokens, etc.)
        strategy_metrics = self.strategy.get_metrics()

        metrics = {
            "strategy": settings.SUMMARIZATION_STRATEGY,
            "total_process_time_ms": f"{total_inference_time_ms:.2f}",  # Tempo total de ponta a ponta
            "total_inference_time_ms": f"{strategy_metrics.get('total_inference_time_ms', 0.0):.2f}",
            # Tempo real gasto no modelo
            "chunks_count": len(chunk_results),
            "avg_time_per_chunk_ms": f"{total_chunk_time_ms / len(chunk_results):.2f}" if chunk_results else "0.00",
            # Detalhes do modelo (tokens, etc.)
            **strategy_metrics,
        }

        logger.info("Métricas finais geradas.", extra=metrics)
        return metrics