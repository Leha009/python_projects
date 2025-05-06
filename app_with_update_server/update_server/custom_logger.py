import sys
import traceback

from datetime import datetime
from enum import IntEnum

class LogLevel(IntEnum):
    NONE = -1
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

class Logger():
    def __init__(
        self,
        name: str,
        log_level: LogLevel = LogLevel.INFO,
        filename: str = None,
        filemode: str = None,
        print_to_console: bool = False
    ) -> None:
        self._name = name
        self._log_level = log_level
        self._filename = filename
        self._filemode = filemode
        self._print_to_console = print_to_console

        if self._filename is not None and self._filemode is None:
            raise ValueError("filemode must be specified if filename is specified")

        self.debug("Logger initialized")

    def log(self, message: str, log_level: LogLevel) -> None:
        if log_level < self._log_level:
            return

        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{now_time} - {log_level.name}] {self._name}: {message}"

        if self._filename is not None:
            with open(self._filename, self._filemode) as f:
                f.write(log_message + "\n")

        if self._print_to_console:
            print(log_message)

    def debug(self, message: str) -> None:
        self.log(message, LogLevel.DEBUG)

    def info(self, message: str) -> None:
        self.log(message, LogLevel.INFO)

    def warning(self, message: str) -> None:
        self.log(message, LogLevel.WARNING)

    def error(self, message: str, *, exc_info: bool = False) -> None:
        self.log(message, LogLevel.ERROR)
        if exc_info:
            self.__output_exception()

    def critical(self, message: str, *, exc_info: bool = False) -> None:
        self.log(message, LogLevel.CRITICAL)
        if exc_info:
            self.__output_exception()

    def __output_exception(self) -> None:
        exc_info = sys.exc_info()
        if None in exc_info:
            return

        if self._filename is not None:
            with open(self._filename, self._filemode) as f:
                traceback.print_exception(*exc_info, file=f)

        if self._print_to_console:
            traceback.print_exception(*exc_info, file=sys.stdout)

    def get_level(self) -> LogLevel:
        return self._log_level

    def set_level(self, log_level: LogLevel) -> None:
        self._log_level = log_level

    def get_filename(self) -> str:
        return self._filename

    def get_filemode(self) -> str:
        return self._filemode

    def set_file(self, filename: str, filemode: str) -> None:
        self._filename = filename
        self._filemode = filemode

    def is_print_to_console_enabled(self) -> bool:
        return self._print_to_console

    def set_print(self, print_to_console: bool) -> None:
        self._print_to_console = print_to_console
