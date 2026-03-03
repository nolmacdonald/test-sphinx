"""Logging configuration utilities for ditto.

Provides a simple function to configure Python's standard logging module
with sensible defaults suitable for library and application use.
"""

from __future__ import annotations

import logging
import sys

# Format used for INFO and above: timestamp, level, logger name, message.
_DEFAULT_FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

# Extended format used for DEBUG: adds source file and line number to aid
# in pinpointing the exact call site during development.
_DEBUG_FMT = "%(asctime)s [%(levelname)s] %(name)s %(filename)s:%(lineno)d: %(message)s"

_DEFAULT_DATEFMT = "%Y-%m-%dT%H:%M:%S"


class _LevelFormatter(logging.Formatter):
    """Formatter that enriches DEBUG records with file name and line number.

    Records at ``DEBUG`` level are formatted with
    ``%(filename)s:%(lineno)d`` so that the call site is immediately
    visible during development.  All other levels use the standard format.
    """

    def __init__(self, fmt: str, datefmt: str) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self._default_fmt = fmt

    def format(self, record: logging.LogRecord) -> str:
        # Temporarily swap the format string for DEBUG records.
        if record.levelno == logging.DEBUG:
            self._style._fmt = _DEBUG_FMT
        else:
            self._style._fmt = self._default_fmt
        return super().format(record)


def configure_logging(
    level: int = logging.INFO,
    fmt: str = _DEFAULT_FMT,
    datefmt: str = _DEFAULT_DATEFMT,
    force: bool = False,
) -> None:
    """Configure the root logger with a StreamHandler writing to stdout.

    Call this once at the entry point of an application that uses ditto.
    Library code should *not* call this function; it is intended for
    end-user scripts and CLI entry points.

    Mirrors the semantics of :func:`logging.basicConfig`: if the root logger
    already has handlers, this function is a no-op unless ``force=True``.

    At ``DEBUG`` level the log format automatically includes the source
    file name and line number (``%(filename)s:%(lineno)d``) to make it
    easier to trace messages back to their call site.  All other levels
    use the standard ``fmt`` format string.

    Parameters
    ----------
    level : int, optional
        Logging level (e.g. ``logging.DEBUG``, ``logging.INFO``), by default
        ``logging.INFO``.
    fmt : str, optional
        Log record format string accepted by :class:`logging.Formatter`.
        Used for all levels except ``DEBUG``, which always includes the
        source file and line number.
    datefmt : str, optional
        Date/time format string for the formatter, by default ISO-8601
        ``"%Y-%m-%dT%H:%M:%S"``.
    force : bool, optional
        When ``True``, remove any existing handlers before configuring.
        Use this to reconfigure logging in scripts that may have pre-existing
        handlers. By default ``False``.

    Examples
    --------
    >>> from ditto.logging_config import configure_logging
    >>> configure_logging(level=logging.DEBUG)
    """
    root_logger = logging.getLogger()

    # Mirror logging.basicConfig semantics: skip setup if handlers already
    # exist unless the caller explicitly requests a forced reconfiguration.
    if root_logger.handlers and not force:
        return

    if force:
        # Remove existing handlers only when the caller explicitly opts in,
        # to avoid unexpectedly discarding file handlers or structured loggers.
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = _LevelFormatter(fmt=fmt, datefmt=datefmt)
    handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(handler)
