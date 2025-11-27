from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações do ambiente e da aplicação."""

    # 1. Configurações Globais
    PROJECT_NAME: str = "SumarizacaoInteligente"
    API_V1_STR: str = "/api/v1"

    # 2. Configuração de Estratégia (Alternância via ENVs)
    # Valores possíveis: "local", "external"
    SUMMARIZATION_STRATEGY: str = "local"

    # 3. Configurações de Chunking
    MAX_CHUNK_LENGTH: int = 1000  # Tamanho máximo de tokens/chars por chunk [cite: 19]
    CHUNK_OVERLAP: int = 50  # Sobreposição entre chunks

    # 4. Configurações do Modelo Local (Exemplo: T5 pequeno)
    LOCAL_MODEL_NAME: str = "t5-small"

    # 5. Configurações do Modelo Externo (Exemplo: Gemini)
    EXTERNAL_API_KEY: str = "AIzaSyBWk00kvO13XrlMmve1Fo0bjVzO7b7Hahs"
    EXTERNAL_MODEL_NAME: str = "gemini-2.5-flash"

    # Configurações de logging, etc.

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()