import os
import logging
import structlog
from datetime import datetime

class CustomLogger:
    """Structured JSON logger backed by structlog + stdlib logging.

    Outputs machine-readable JSON lines to both the console and a timestamped
    log file. Configuration is applied once per process regardless of how many
    times the class is instantiated.

    Usage::

        logger = CustomLogger().get_logger(__file__)
        logger.info("event description", key="value")
    """

    _configured = False

    def __init__(self, log_dir: str = "logs"):
        """Initialize the logger and configure handlers on first use.

        Args:
            log_dir: Directory where log files are stored, relative to project root.
        """
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.logs_dir = os.path.join(root_dir, log_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        log_file_name = f"log_{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file_name)

        if not CustomLogger._configured:
            self._configure()
            CustomLogger._configured = True

    def _configure(self) -> None:
        """Set up stdlib handlers and structlog processor pipeline. Called once."""
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[file_handler, console_handler],
        )

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def get_logger(self, name: str) -> structlog.stdlib.BoundLogger:
        """Return a structured logger tagged with the calling module's filename.

        Args:
            name: Typically ``__file__`` of the calling module.
        """
        return structlog.get_logger(os.path.basename(name))

if __name__ == "__main__":
    logger = CustomLogger().get_logger(__file__)
    logger.info("User uploaded a file", user_id=123, filename="report.pdf")
    logger.error("Failed to process PDF", error="File not found",  user_id=123)