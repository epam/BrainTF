import logging
import os
from logging import Logger

log_level = os.environ.get("LOG_LEVEL", "INFO")
logger: Logger = logging.getLogger(name="braintf")
logger.setLevel(log_level)
