import logging
import traceback
from app.utils.config import settings


def get_logger(name: str = "FaceBookAPI"):
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(settings.LOG_LEVEL)  # ex: "INFO"
    logger.propagate = False  # prevents double logs with uvicorn

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # ✅ File handler (app.log)
    file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
    file_handler.setLevel(settings.LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # ✅ Console handler (terminal)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.LOG_LEVEL)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = get_logger()

# traceback
def log_exception(e: Exception, extra: str = ""):

    trace = traceback.format_exc()

    if extra:
        logger.error(f"{extra} | {e}\n{trace}")
    else:
        logger.error(f"{e}\n{trace}")