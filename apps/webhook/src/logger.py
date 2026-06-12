from typing import Any

from loguru import logger


class AppLogger:
    _configured = False

    def __init__(self) -> None:
        if not self.__class__._configured:
            logger.remove()

            logger.add(
                sink=lambda msg: print(msg, end=""),
                level="INFO",
                colorize=True,
                enqueue=True,
            )

            self.__class__._configured = True

    def bind(self, **kwargs: dict) -> Any:
        return logger.bind(**kwargs)

    def info(self, message: str, **kwargs: dict) -> None:
        logger.bind(**kwargs).info(message)

    def error(self, message: str, **kwargs: dict) -> None:
        logger.bind(**kwargs).error(message)

    def warning(self, message: str, **kwargs: dict) -> None:
        logger.bind(**kwargs).warning(message)


app_logger: AppLogger = AppLogger()
