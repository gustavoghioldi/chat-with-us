import logging

db_default_formatter = logging.Formatter()


class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from .models import StatusLog

        trace = None

        if record.exc_info:
            trace = db_default_formatter.formatException(record.exc_info)

        message = record.getMessage()

        kwargs = {
            "level": record.levelno,
            "logger": record.name,
            "message": message,
            "pathname": record.pathname,
            "funcname": record.funcName,
            "lineno": record.lineno,
            "trace": trace
        }

        StatusLog.objects.create(**kwargs)