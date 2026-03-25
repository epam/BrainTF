import logging
from logging import Logger


logger: Logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add stream handler to output logs to console
# handler = logging.StreamHandler()
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)


