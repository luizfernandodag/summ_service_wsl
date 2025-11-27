from fastapi import FastAPI, HTTPException
from .tools.summarization_tool import summarize_text, SUMMARIZE_TEXT_MANIFEST
from mcp_server.schemas import SummarizeTextInput

from app.core.logger import logger

import json

app = FastAPI(
    title="MCP Server - Sumarização Inteligente",
    description="Servidor que expõe ferramentas de IA para consumo por Large Language Models (LLMs)."
)

# O Dicionário de Ferramentas disponíveis
AVAILABLE_TOOLS = {
    "summarize_text": summarize_text
}

import time
import os

@app.get("/health", include_in_schema=False)
async def health_check():
    start = time.time()
    status = {
        "status": "ok",
        "uptime_ms": round((time.time() - start) * 1000, 2),
        "strategy": os.getenv("SUMMARIZATION_STRATEGY", "undefined"),
    }
    return status

@app.get("/mcp.json", include_in_schema=False)
async def get_mcp_manifest():
    """
    Endpoint de descoberta do Model Context Protocol (MCP).
    Deve retornar o JSON de configuração que o cliente (ex: ChatGPT) irá consumir.
    """

    # Arquitetura do MCP Server (requisito)
    manifest = {
        "schema_version": "1.0.0",
        "name": "SummarizationToolProvider",
        "description": "Um conjunto de ferramentas para processamento e sumarização de textos longos.",
        "tools": [SUMMARIZE_TEXT_MANIFEST],
        "contact": "support@example.com"
    }
    logger.info("Manifest MCP solicitado.", extra={"tools_count": len(manifest['tools'])})
    return manifest


@app.post(SUMMARIZE_TEXT_MANIFEST["endpoint"])
async def run_summarize_text(input_data: SummarizeTextInput):
    """
    Endpoint real para execução da ferramenta 'summarize_text'.
    """
    try:
        # Chama a função Python assíncrona da ferramenta
        result = await summarize_text(input_data)

        # O modelo .model_dump() é usado para garantir a saída JSON pura
        return result.model_dump()

    except Exception as e:
        logger.error(f"Erro no endpoint de execução da ferramenta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Rodar este servidor: uvicorn mcp_server.server:app --port 8080 --reload