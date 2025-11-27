import logging
import sys
from pythonjsonlogger import jsonlogger

# Configuração básica do logger
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s"


def setup_logger(name: str):
    """
    Configura e retorna um logger com formato JSON.
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Previne a propagação para o root logger
    if not logger.handlers:
        # Handler para saída padrão
        handler = logging.StreamHandler(sys.stdout)

        # Formato JSON (structured logs)
        formatter = jsonlogger.JsonFormatter(LOG_FORMAT)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


logger = setup_logger("SummarizationService")