import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)

handler = logging.FileHandler('logs/request_logs.json')
format_str = '%(msg)s %(asctime)s %(name)s %(levelname)s %(thread)s'
formatter = jsonlogger.JsonFormatter(format_str)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
