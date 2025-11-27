# Dockerfile (corrigido)
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# garante gunicorn/uvicorn caso não esteja no requirements
RUN pip install --no-cache-dir gunicorn uvicorn

# Baixa pacotes NLTK necessários durante o build (para não falhar em runtime)
RUN python -c "import nltk; nltk.download('punkt_tab', download_dir='/usr/local/lib/python3.11/site-packages/nltk_data')"
ENV NLTK_DATA=/usr/local/lib/python3.11/site-packages/nltk_data

FROM python:3.11-slim AS runner
WORKDIR /app
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PORT_MAIN=8000
ENV PORT_MCP=8080

# runtime deps
RUN apt-get update && apt-get install -y \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# copia dependências instaladas
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
RUN chmod +x /usr/local/bin/gunicorn /usr/local/bin/uvicorn

# copia código
COPY . .

# NLTK data durante build (evita baixar no runtime)
RUN python -c "import nltk; nltk.download('punkt', download_dir='/usr/local/lib/python3.11/site-packages/nltk_data')"
ENV NLTK_DATA=/usr/local/lib/python3.11/site-packages/nltk_data

# Comando padrão da imagem (usa sh -c pra expandir ${PORT_MAIN})
CMD ["sh", "-c", "gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT_MAIN}"]
