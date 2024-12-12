import logging
import sys

from colored_custom_logger import ColoredFormatter  # type: ignore[import-untyped]


class Logger:
    __logger: logging.Logger

    def __init__(self) -> None:
        self.__logger = self.__create_set_logger()

    def __create_set_logger(self) -> logging.Logger:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())

        for handler in (console_handler,):
            logger.addHandler(handler)

        return logger

    def __call__(self) -> logging.Logger:
        return self.__logger
