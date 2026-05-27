import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if not settings.DEBUG:
        handlers.append(logging.FileHandler("logs/app.log"))

    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
    )


logger = logging.getLogger("career_platform")
