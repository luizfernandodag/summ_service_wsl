#!/bin/bash
set -e

PROJECT_NAME="summarization-service"
REPO_URL="git@github.com:luizfernandodag/summ_service_wsl.git"

echo "📦 Criando projeto em: $PROJECT_NAME"
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

#########################################
# 1) AMBIENTE VIRTUAL
#########################################
echo "🐍 Criando ambiente virtual Python..."
python3 -m venv venv

echo "⚙️ Ativando venv..."
source venv/bin/activate

#########################################
# 2) ESTRUTURA DE DIRETÓRIOS
#########################################
echo "📁 Criando estrutura de diretórios..."

mkdir -p app/api/v1
mkdir -p app/core
mkdir -p app/services
mkdir -p app/strategies

mkdir -p mcp_server/tools

mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/fixtures

#########################################
# 3) ARQUIVOS BASE
#########################################

echo "📝 Criando arquivos do projeto..."

# ========== app ==========
cat > app/main.py <<EOF
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}
EOF

cat > app/api/v1/summarization.py <<EOF
from fastapi import APIRouter

router = APIRouter()

@router.post("/summarize")
def summarize(payload: dict):
    return {"summary": "Not implemented"}
EOF

cat > app/core/config.py <<EOF
class Settings:
    APP_NAME: str = "Summarization Service"
    VERSION: str = "1.0.0"

settings = Settings()
EOF

cat > app/core/logger.py <<EOF
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("summarization_service")
EOF

cat > app/services/summarizer.py <<EOF
class SummarizerService:
    def run(self, text: str) -> str:
        return "summary not implemented"
EOF

cat > app/services/text_processor.py <<EOF
class TextProcessor:
    def clean(self, text: str) -> str:
        return text
EOF

cat > app/strategies/base.py <<EOF
from abc import ABC, abstractmethod

class SummarizationStrategy(ABC):

    @abstractmethod
    def summarize(self, text: str) -> str:
        pass
EOF

cat > app/strategies/local_transformer.py <<EOF
from .base import SummarizationStrategy

class LocalTransformerStrategy(SummarizationStrategy):
    def summarize(self, text: str) -> str:
        return "local transformer summary"
EOF

cat > app/strategies/external_llm_api.py <<EOF
from .base import SummarizationStrategy

class ExternalLLMStrategy(SummarizationStrategy):
    def summarize(self, text: str) -> str:
        return "external LLM summary"
EOF

# ========== MCP ==========
cat > mcp_server/server.py <<EOF
# Placeholder para servidor MCP
print("MCP Server not implemented yet.")
EOF

cat > mcp_server/README_MCP.md <<EOF
# MCP Server
Instruções de uso serão adicionadas posteriormente.
EOF

#########################################
# 4) .gitignore e .dockerignore
#########################################

echo "📄 Criando .gitignore e .dockerignore..."

cat > .gitignore <<EOF
venv/
__pycache__/
*.pyc
.env
.DS_Store
.idea/
.vscode/
EOF

cat > .dockerignore <<EOF
venv/
__pycache__/
*.pyc
.git/
.env
.DS_Store
.idea/
.vscode/
EOF

#########################################
# 5) Dockerfile
#########################################

echo "🐳 Criando Dockerfile..."

cat > Dockerfile <<EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

#########################################
# 6) docker-compose
#########################################

echo "🐳 Criando docker-compose.yml..."

cat > docker-compose.yml <<EOF
services:
  web:
    build: .
    container_name: summarization_service
    ports:
      - "8000:8000"
    env_file:
      - .env
EOF

#########################################
# 7) requirements
#########################################

echo "📦 Criando requirements.txt..."

cat > requirements.txt <<EOF
fastapi
uvicorn
EOF

#########################################
# 8) README
#########################################

cat > README.md <<EOF
# summ_service_wsl

Serviço de sumarização com FastAPI + WSL + Docker.
EOF

#########################################
# 9) GIT – init + push
#########################################

echo "🔗 Inicializando repositório Git..."

git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin $REPO_URL

echo "⬆️ Enviando para o GitHub..."
git push -u origin main

#########################################
echo "✨ Projeto criado com sucesso!"
echo "Ative o ambiente virtual com:"
echo "source venv/bin/activate"
#########################################
