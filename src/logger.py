import datetime
import gzip
import logging.handlers
import shutil

from pythonjsonlogger import jsonlogger


class ExcludeDockerHealthCheckFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'headers'):
            return record.headers.get('healthcheck-header') != 'healthcheck-message'
        return True


def namer(name):
    now = datetime.datetime.now()
    return f'{name}_{now.strftime("%d-%m-%y_%H-%M")}.gz'


def rotator(source, dest):
    with open(source, 'rb') as file_in:
        with gzip.open(dest, 'wb') as file_out:
            shutil.copyfileobj(file_in, file_out)


logger = logging.getLogger(__name__)
max_bytes = 50 * 1024 * 1024

handler = logging.handlers.RotatingFileHandler('logs/request_logs.json', maxBytes=max_bytes, backupCount=10)
handler.addFilter(ExcludeDockerHealthCheckFilter())
handler.namer, handler.rotator = namer, rotator
format_str = '%(msg)s %(asctime)s %(name)s %(levelname)s %(thread)s'
formatter = jsonlogger.JsonFormatter(format_str)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
