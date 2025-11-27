import pytest
import respx
from unittest.mock import MagicMock, patch
from ...app.services.summarizer import SummarizationService
from ...app.core.config import settings
from ...app.strategies.base import SummarizationStrategy


# Fixture de texto de teste para simular uma entrada longa
@pytest.fixture
def long_text():
    return "A primeira parte do texto é sobre a introdução. " * 10 + \
        "A segunda parte é sobre os métodos avançados de IA e ML. " * 10 + \
        "A terceira parte aborda a conclusão final do estudo." * 10


# Mock da classe base para simular a sumarização sem chamar o modelo real
class MockStrategy(SummarizationStrategy):
    def summarize_chunk(self, text: str) -> str:
        # Simula um processamento síncrono
        import time
        time.sleep(0.01)
        return f"Resumo simulado para chunk: {text[:20]}..."

    def get_metrics(self) -> dict:
        return {
            "strategy": settings.SUMMARIZATION_STRATEGY,
            "total_inference_time_ms": 100.0,  # Valor fixo para o mock
            "total_tokens_processed": 500,
        }


# Mock para garantir que a estratégia correta seja carregada
@patch("app.services.summarizer.ExternalLLMSummarization", new=MockStrategy)
@patch("app.services.summarizer.LocalTransformerSummarization", new=MockStrategy)
@pytest.mark.asyncio
async def test_summarize_service_metrics(long_text):
    """Testa o fluxo completo e verifica se as métricas estão corretas."""

    # Testa a estratégia LOCAL
    settings.SUMMARIZATION_STRATEGY = "local"
    service_local = SummarizationService()
    result_local = await service_local.summarize(long_text)

    # 1. Verifica o resumo
    assert "Resumo simulado" in result_local['summary']

    # 2. Verifica as métricas globais
    metrics = result_local['metrics']
    assert metrics['strategy'] == 'local'
    assert metrics['chunks_count'] > 1
    assert float(metrics['total_process_time_ms']) > 0
    assert float(metrics['avg_time_per_chunk_ms']) > 0
    assert metrics['total_tokens_processed'] == 500  # Valor do Mock

    # Testa a estratégia EXTERNAL
    settings.SUMMARIZATION_STRATEGY = "external"
    service_external = SummarizationService()
    result_external = await service_external.summarize(long_text)

    # 3. Verifica a alternância de estratégia
    assert result_external['metrics']['strategy'] == 'external'


@pytest.mark.asyncio
async def test_api_endpoint_success(client, long_text, monkeypatch):
    """Testa se o endpoint da API retorna 200 e a estrutura correta."""

    # Mocka a estratégia para que o teste não precise de chaves ou modelos reais
    def mock_load_strategy(*args, **kwargs):
        return MockStrategy()

    monkeypatch.setattr(SummarizationService, '_load_strategy', mock_load_strategy)

    response = await client.post(
        "/api/v1/summarize",
        json={"text": long_text}
    )

    assert response.status_code == 200
    data = response.json()

    # Verifica a estrutura da resposta (conforme Pydantic)
    assert "summary" in data
    assert "metrics" in data
    assert "strategy" in data
    assert data['strategy'] == settings.SUMMARIZATION_STRATEGY  # O valor do env atual
    assert data['summary'].startswith("Resumo simulado")

    # Verifica logs estruturados (não é um teste de cobertura, mas é importante)
    # Isso seria feito testando a saída do logger, mas aqui verificamos a resposta
    assert "chunks_count" in data['metrics']