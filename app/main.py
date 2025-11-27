from fastapi import FastAPI
from .api.v1 import summarization
from .core.config import settings
from .core.logger import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0"
)

# Inclui os endpoints da API
app.include_router(summarization.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Executado na inicialização da aplicação."""
    logger.info("Serviço de Sumarização Inteligente iniciado.",
                extra={"strategy_mode": settings.SUMMARIZATION_STRATEGY})

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Serviço de Sumarização Inteligente. Acesse /docs para a documentação da API."}

# Para rodar: uvicorn app.main:app --reload