# mcp_server/tools/summarization_tool.py
from pydantic import BaseModel
from typing import Any, Dict

# Use imports absolutos (assume package root contains "app" package)
from app.services.summarizer import SummarizationService
from app.core.logger import logger
from mcp_server.schemas import SummarizeTextInput, SummarizeTextOutput

# inicializa o serviço (pode carregar estratégia via .env)
summarizer = SummarizationService()


async def summarize_text(input_data: SummarizeTextInput) -> SummarizeTextOutput:
    """
    Sumariza um texto longo usando o sistema de sumarização inteligente.
    Função exposta pelo MCP.
    """
    try:
        logger.info("Ferramenta summarize_text acionada pelo cliente MCP.")

        # Se SummarizationService.summarize for síncrono, remova await.
        result = await summarizer.summarize(input_data.text)

        summary = result.get("summary", "Resumo indisponível.")
        logger.info(
            "Sumarização concluída via MCP.",
            extra={
                "strategy_used": result.get("metrics", {}).get("strategy"),
                "chunk_count": result.get("metrics", {}).get("chunks_count"),
            },
        )

        return SummarizeTextOutput(summary=summary)

    except Exception as e:
        logger.exception("Erro ao executar summarize_text via MCP")
        return SummarizeTextOutput(
            summary=f"ERRO: Não foi possível resumir o texto: {str(e)}"
        )


# Manifest da ferramenta (para MCP)
SUMMARIZE_TEXT_MANIFEST = {
    "name": "summarize_text",
    "description": "Ferramenta para resumir documentos e textos longos.",
    "input_schema": SummarizeTextInput.model_json_schema(),
    "output_schema": SummarizeTextOutput.model_json_schema(),
    "endpoint": "/v1/tools/summarize_text",
    "http_method": "POST",
}
