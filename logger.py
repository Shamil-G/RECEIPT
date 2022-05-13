import logging
import logging.config
from logging.handlers import RotatingFileHandler
import app_config as cfg


def init_service_logger():
    logger = logging.getLogger('RECEIPT-SERVICE')
    # logging.getLogger('PDD').addHandler(logging.StreamHandler(sys.stdout))
    # Console
    logging.getLogger('RECEIPT-SERVICE').addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("service.log", encoding="UTF-8")
    # fh = RotatingFileHandler(cfg.LOG_FILE, encoding="UTF-8", maxBytes=100000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.info('RECEIPT-SERVICE Logging started')
    return logger


log = init_service_logger()
