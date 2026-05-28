import logging
from pathlib import Path


def setup_logging():
    """Setup logging for all app."""

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "app.log"),
            logging.FileHandler(log_dir / "yookassa_webhook.log")
        ]
    )

    logging.getLogger("yookassa").setLevel(logging.DEBUG)
    logging.getLogger("stripe").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    yookassa_logger = logging.getLogger("app.modules.private_modules.payment.yookassa")
    yookassa_logger.setLevel(logging.DEBUG)

    return logging.getLogger(__name__)

logger = logging.getLogger(__name__)
