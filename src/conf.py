from enum import Enum
from logging import Formatter, Logger, getLogger
from logging.handlers import RotatingFileHandler


class LoggingLevels(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class CustomLogger:
    _logger: Logger

    def __init__(
        self,
        filename: str,
        loggerName: str = None,
        level: LoggingLevels = LoggingLevels.INFO.value,
        backupCount: int = 5,
        formatter: Formatter = Formatter(
            "%(asctime)s %(levelname)s -- %(funcName)s(%(lineno)d) - %(message)s"
        ),
    ) -> Logger:
        """_summary_

        Args:
            filename (str): Название файла
            loggerName (str, optional): Название логгера. По умолчанию равно имени файла.
            level (int, optional): Уровень логирования по системе logging. По умолчанию равно INFO.
            backupCount (int, optional): Количество бекапов файлов. По умолчанию равно 5 файлам.
            formatter (Formatter, optional): Формат логов, по умолчанию Formatter("%(asctime)s %(levelname)s -- %(funcName)s(%(lineno)d) - %(message)s").
        """
        if not loggerName:
            loggerName = filename
        self._logger = getLogger(loggerName)
        self._logger.level = level
        self._logger.propagate = False

        handler = RotatingFileHandler(
            filename=f"{filename}.log",
            maxBytes=(5 * 1024 * 1024),
            backupCount=backupCount,
            encoding="utf-8",
        )

        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
