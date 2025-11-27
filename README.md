# 🧠 Sistema de Sumarização Inteligente  
**Arquitetura Profissional – IA, FastAPI, Docker e MCP Server**

Este projeto implementa um sistema de **alta performance para sumarização de textos longos**, com suporte a:

- Estratégia **Local** (modelos Transformers)
- Estratégia **Externa** (APIs de LLMs, como Google Gemini)
- **Logs estruturados** para observabilidade
- **Estratégias intercambiáveis via `.env`**
- **Servidor MCP (Model Context Protocol)** para integração com LLMs como ChatGPT

Totalmente conteinerizado com **Docker**, garantindo execução confiável em qualquer ambiente.

---

# 🚀 1. Configuração e Execução

A forma preferencial de rodar o projeto é via **Docker Compose**, garantindo portabilidade e reprodutibilidade.

---

## 📌 1.1. Pré-requisitos

- Docker  
- Docker Compose  
- Chave de API (somente se usar a estratégia `external`)

---

## 📌 1.2. Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
# Estratégia de sumarização: 'local' ou 'external'
SUMMARIZATION_STRATEGY=external

# API Externa (somente se SUMMARIZATION_STRATEGY=external)
EXTERNAL_API_KEY="SUA_CHAVE_AQUI"
EXTERNAL_MODEL_NAME="gemini-2.5-flash"

# Chunking
MAX_CHUNK_LENGTH=1000
CHUNK_OVERLAP=50
```

Para usar a estratégia local:

```env
SUMMARIZATION_STRATEGY=local
```

---

## 📌 1.3. Rodar com Docker Compose

O projeto sobe dois serviços:

| Serviço             | Porta | Descrição                      |
|--------------------|-------|--------------------------------|
| summarization_app  | 8000  | API principal de sumarização   |
| mcp_server         | 8080  | Servidor MCP para LLMs         |

### ▶️ Construir e iniciar

```bash
docker compose up --build -d
```

### Ver processos

```bash
docker compose ps
```

### Ver logs

```bash
docker compose logs -f summarization_app
docker compose logs -f mcp_server
```

### Parar

```bash
docker compose down
```

---

# 🌐 2. Endpoints Principais

## 📘 API de Sumarização (FastAPI)

Swagger UI:

```
http://localhost:8000/api/v1/docs
```

Healthcheck:

```
http://localhost:8000/health
```

## 🔗 MCP Server

Manifesto MCP:

```
http://localhost:8080/mcp.json
```

Ferramenta MCP disponível:

```
summarize_text
```

Endpoint de execução:

```
POST http://localhost:8080/v1/tools/summarize_text
```

---

# 🏛️ 3. Arquitetura e Organização

O projeto segue princípios de **Clean Architecture**, **SOLID** e **alta modularidade**.

```
app/
 ├── api/               # Rotas FastAPI e validações
 ├── services/          # Orquestra lógica, paralelismo e chunking
 ├── strategies/        # Estratégias de IA (local/external)
 ├── core/              # Logger, configs e utilidades

mcp_server/
 ├── server.py          # Servidor MCP
 ├── tools/             # Ferramentas MCP
 ├── schemas.py         # Modelos Pydantic

tests/
```

---

# ⚡ 4. Performance e Escalabilidade

## Processamento Assíncrono

- asyncio  
- anyio.to_thread.run_sync  
- TaskGroups  

## Chunking Inteligente

- Divisão por sentenças  
- Overlap configurável  

## Deploy Otimizado

- Gunicorn  
- Uvicorn Workers  
- Multi-stage build  

---

# 📊 5. Observabilidade

## Logs Estruturados em JSON

Compatível com Grafana Loki, Elastic Stack, Datadog e Prometheus.

## Métricas incorporadas

- total_process_time_ms  
- inference_time_ms  
- chunks_count  
- avg_time_per_chunk_ms  
- total_input_tokens  
- total_output_tokens  

---

# 🧪 6. Testes Automatizados

Localizados em:

```
tests/
```

Executar:

```bash
pytest -q
```

---

# 🔗 7. MCP Server – Model Context Protocol

Ferramentas disponíveis:

| Ferramenta       | Função                                      |
|------------------|----------------------------------------------|
| summarize_text   | Resume textos via pipeline principal          |

Arquivo detalhado:

```
mcp_server/README_MCP.md
```

---

# 🧪 8. Exemplo de Execução MCP

```bash
curl -sS -X POST http://localhost:8080/v1/tools/summarize_text   -H "Content-Type: application/json"   -d '{"text":"Texto teste."}' | jq .
```

Saída esperada:

```json
{
  "summary": "Texto de teste."
}
```