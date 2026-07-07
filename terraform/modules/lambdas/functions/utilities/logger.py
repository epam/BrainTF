import logging
import os
from logging import Logger

log_level = os.environ.get("LOG_LEVEL", "INFO")
logger: Logger = logging.getLogger()
logger.setLevel(log_level)
