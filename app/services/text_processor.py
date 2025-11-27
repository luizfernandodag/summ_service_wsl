import nltk
from typing import List
from ..core.config import settings
from ..core.logger import logger

# Garante que o pacote 'punkt' (para tokenização de sentenças) esteja baixado
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')


class TextProcessor:
    """
    Responsável pela limpeza, divisão em chunks e unificação de texto.
    """

    def __init__(self):
        self.max_len = settings.MAX_CHUNK_LENGTH
        self.overlap = settings.CHUNK_OVERLAP

    def split_into_chunks(self, text: str) -> List[str]:
        """
        Divide um texto longo em chunks com base em sentenças,
        adicionando sobreposição para manter o contexto.
        """
        if not text:
            return []

        # 1. Tokenização de Sentenças
        # Usamos sentenças como base para evitar quebrar palavras no meio.
        sentences = nltk.sent_tokenize(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            # Se a sentença atual + o chunk atual exceder o limite,
            # finaliza o chunk e inicia um novo.
            if current_length + sentence_len > self.max_len:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))

                    # 2. Implementação da Sobreposição (Overlap)
                    # Adiciona as últimas sentenças do chunk anterior ao novo chunk
                    # para dar contexto ao modelo.
                    overlap_sentences_count = max(1, len(current_chunk) // (self.overlap // 20))
                    current_chunk = current_chunk[-overlap_sentences_count:]
                    current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_len + 1  # +1 para o espaço

        # Adiciona o último chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        logger.info(f"Texto dividido em {len(chunks)} chunks.",
                    extra={"chunks_count": len(chunks), "max_len": self.max_len})

        return chunks

    def unify_summaries(self, summaries: List[str]) -> str:
        """
        Método para unificar os resumos individuais em um único resumo final coerente.

        NOTA: Em um projeto avançado, esta etapa deveria usar o LLM novamente 
        (map-reduce) para resumir os resumos, mas para este desafio, 
        vamos concatená-los para simplificar a unificação.
        """

        if not summaries:
            return ""

        # Simples unificação com quebras de linha (pode ser melhorado com LLM)
        final_summary = "\n\n".join(summaries)

        logger.info("Resumos unificados em um único documento.")

        return final_summary