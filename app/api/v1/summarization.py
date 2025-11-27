from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...services.summarizer import SummarizationService
from ...core.logger import logger

router = APIRouter()
summarizer_service = SummarizationService()


# 1. Modelo de Entrada (Schema Pydantic)
class SummarizationRequest(BaseModel):
    """Schema para a requisição de sumarização."""
    text: str = Field(..., description="O texto longo a ser sumariado.", min_length=50)


# 2. Modelo de Saída (Schema Pydantic)
class SummarizationResponse(BaseModel):
    """Schema para a resposta da sumarização."""
    summary: str = Field(..., description="O resumo coerente gerado.")
    metrics: dict = Field(..., description="Métricas de desempenho e inferência (tempo, tokens).")
    strategy: str = Field(..., description="Estratégia de sumarização utilizada ('local' ou 'external').")


@router.post("/summarize", response_model=SummarizationResponse, status_code=200)
async def summarize_text(request: SummarizationRequest):
    """
    Endpoint principal para receber um texto e retornar um resumo,
    utilizando a estratégia de sumarização configurada via ENV.
    """

    logger.info("Requisição de sumarização recebida.")

    # Chama o serviço principal
    result = await summarizer_service.summarize(request.text)

    # Acessa a métrica de estratégia que foi injetada pelo serviço
    strategy_used = result['metrics']['strategy']

    response = SummarizationResponse(
        summary=result['summary'],
        metrics=result['metrics'],
        strategy=strategy_used
    )

    logger.info("Sumarização concluída com sucesso.", extra={"strategy": strategy_used})

    return response