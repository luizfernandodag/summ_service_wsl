import pytest
from ...app.services.text_processor import TextProcessor
from ...app.core.config import settings

# Override das configurações para facilitar o teste de chunking
settings.MAX_CHUNK_LENGTH = 100
settings.CHUNK_OVERLAP = 20


@pytest.fixture
def processor():
    return TextProcessor()


def test_split_into_chunks_empty_text(processor):
    """Deve retornar uma lista vazia para um texto vazio."""
    assert processor.split_into_chunks("") == []
    assert processor.split_into_chunks("    ") == []


def test_split_into_chunks_single_chunk(processor):
    """Deve retornar um único chunk se o texto for curto."""
    short_text = "Esta é uma frase curta. E esta é a segunda."
    chunks = processor.split_into_chunks(short_text)
    assert len(chunks) == 1
    assert chunks[0] == short_text


def test_split_into_chunks_multiple_chunks_with_overlap(processor):
    """
    Deve dividir corretamente em múltiplos chunks e garantir que a sobreposição exista.
    """
    # Criamos um texto longo onde cada sentença tem cerca de 30-40 caracteres.
    long_text = (
            "Sentença 1: O rato roeu a roupa do rei de Roma. " * 2 +  # 1
            "Sentença 2: A rainha ficou furiosa com o ocorrido. " * 2 +  # 2
            "Sentença 3: O rei perdoou o rato, pois ele estava faminto. " * 2 +  # 3
            "Sentença 4: O palácio providenciou um banquete de queijo. " * 2 +  # 4
            "Sentença 5: E assim, todos viveram felizes para sempre. " * 2  # 5
    )
    # Com MAX_CHUNK_LENGTH=100, devemos ter cerca de 3 a 4 chunks.

    chunks = processor.split_into_chunks(long_text)

    # Esperamos pelo menos 3 chunks para este texto
    assert len(chunks) >= 3

    # Verifica a sobreposição: o chunk 2 deve começar com o final do chunk 1
    # O chunking é baseado em sentenças. O final do Chunk 1 (Sentença 2) deve
    # estar no início do Chunk 2.

    # 1. Obter a última sentença do Chunk 1
    last_sentence_chunk1 = chunks[0].split('.')[-2].strip() + '.'

    # 2. Verificar se esta sentença (ou parte dela) está no início do Chunk 2
    # A lógica de overlap no text_processor usa as últimas sentenças.
    assert last_sentence_chunk1 in chunks[1]

    # Verifica se nenhum chunk ultrapassou o limite (aprox.)
    for chunk in chunks:
        assert len(chunk) < settings.MAX_CHUNK_LENGTH + 50  # Tolerância devido ao tamanho da sentença


def test_unify_summaries(processor):
    """Deve unificar a lista de resumos com quebras de linha."""
    summaries = ["Resumo A.", "Resumo B.", "Resumo C."]
    expected = "Resumo A.\n\nResumo B.\n\nResumo C."
    assert processor.unify_summaries(summaries) == expected