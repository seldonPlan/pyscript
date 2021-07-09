"""
Provides python logger, handler, and formatter objects. These components are
configured with some opinionated defaults intended to quickly get up with click
integrated logging.

``getCliLogger`` function is the main entrypoint to the module, and returns the
configured logger instance. Child loggers can be returned by passing a {name} to
this function.

```
log = getCliLogger()
log.warning("foo")

> [ WARN ][ 2021-12-31 23:59:59 ] foo
```

Preset configuration options can be set while calling the ``configRootLogger``.
This function is meant to be called on initialization of the cli application
and provides options for setting the logging level, root logger name, adjusting
logged output formatting, adding additional handlers, and more.

See the ``configRootLogger`` docstring for the full configuration list.

Derived classes ``CliLogHandler`` and ``CliLogFormatter`` are also available to
add click integrated functionality to your own existing loggers.
"""

import json
import logging
from datetime import datetime
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING  # noqa: F401
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Iterable, Optional, Union, cast

import click

# fmt: off
__all__ = [
    "_default_root_name", "_default_timestamp_format", "_default_logger",
    "_default_cli_handler", "_default_file_handler",
    "configRootLogger", "getCliLogger", "verbosity",
    "CliLogFormatter", "CliLogHandler",
    "DEBUG", "WARNING", "INFO", "ERROR", "CRITICAL",
]
# fmt: on

_default_root_name: str = "{{ cookiecutter.project_module }}"
_default_timestamp_format: str = "%Y-%m-%d %H:%M:%S"
_default_logger: Optional[logging.Logger] = None
_default_cli_handler: Optional[logging.Handler] = None
_default_file_handler: Optional[RotatingFileHandler] = None


def _reset_logging(root_name: str):
    # https://stackoverflow.com/a/56810619
    manager = logging.root.manager  # type: ignore
    manager.disabled = logging.NOTSET
    for logger in manager.loggerDict.values():
        if isinstance(logger, logging.Logger) and logger.name.startswith(root_name):
            logger.setLevel(logging.NOTSET)
            logger.propagate = True
            logger.disabled = False
            logger.filters.clear()
            for handler in logger.handlers:
                # Copied from `logging.shutdown`.
                try:
                    handler.acquire()
                    handler.flush()
                    handler.close()
                except (OSError, ValueError):
                    pass
                finally:
                    handler.release()
                logger.removeHandler(handler)


def verbosity(verbose: int, quiet: bool) -> dict[str, Union[str, int]]:
    """Translate verbosity cli options to logging level"""
    if quiet:
        return {"name": "CRITICAL", "value": logging.CRITICAL}

    if verbose == 1:
        return {"name": "INFO", "value": logging.INFO}

    if verbose == 2:
        return {"name": "DEBUG", "value": logging.DEBUG}

    # default level
    return {"name": "WARNING", "value": logging.WARNING}


def configRootLogger(
    level: Union[str, int] = logging.WARNING,
    root_name: str = _default_root_name,
    options: Iterable[str] = None,
    **file_handler_kwargs,
):
    """
    Configure and maintain a reference to a root logger instance. Use in conjunction
    with ``getCliLogger`` to retrieve the logger instance, or child loggers from it.
    This function resets the root logger every time it's called.

    Default logger behavior is listed below along with relevant {options} flags
    that alter these defaults. Supplying the option name in the {options} Iterable
    sets the flag to True, and enables the option description:

     * DEFAULT: logger uses ``CliLogHandler`` to log to STDOUT using ``click.echo``
       - "disable_terminal_log": prevents attachment of a ``CliLogHandler`` instance
       - "log_to_stderr": log to STDERR, instead of STDOUT via ``CliLogHandler``
                    (ignored with {disable_terminal_log})

     * DEFAULT: log lines are prefixed using this format: "[ LEVEL ][ TIMESTAMP ] msg"
       - "hide_prefix": dont generate prefix blocks at all (logs msg only)
       - "dense_output": apply a prefix line to every message line, not just the first
                    (ignored with {hide_prefix})
       - "add_channel": add a logging channel name prefix block
                    (ignored with {hide_prefix})
       - "add_debug_fileref": add a relative filename/line number prefix block for
                    DEBUG level log lines
                    (ignored with {hide_prefix})
       - "prefix_own_line": print the log prefix on its own line, followed by any
                    message lines
                    (ignored with {hide_prefix} and {dense_output})

     * DEFAULT: logged dict objects are converted to compact json with ``json.dumps``
       - "disable_dict_to_json": disables dict conversion to json strings
       - "pretty_print_json": output dict objects as "pretty-printed" json instead
                    (ignored with {disable_dict_to_json})

     * DEFAULT: timestamp for log entries uses strftime format: "%Y-%m-%d %H:%M:%S".
       - "ts_use_full": formats log timestamp with fractional seconds
       - "ts_use_relative": formats log timestamp as relative millis since startup
       - "ts_use_epoch": formats log timestamp as millis since epoch

    :param level: logging level for root logger (defaults to "WARNING")
    :param root_name: root logger name (defaults to ``_default_root_name`` value)
    :param options: array of option flag names (see option descriptions listed above)
    :param file_handler_kwargs: attach a ``RotatingFileHandler`` instance to root logger
            {filename} must be present in kwargs, all other params are optionally
            applied against these defaults:
            ``(filename={filename}, maxBytes=10000000, backupCount=5, encoding="utf8")``
    """
    global _default_logger
    global _default_cli_handler
    global _default_file_handler

    _log_opts: list[str] = [] if options is None else list(options)
    _log_opts = [flag.lower() for flag in _log_opts]
    _options = {
        "disable_terminal_log": "disable_terminal_log" in _log_opts,
        "log_to_stderr": "log_to_stderr" in _log_opts,
        "dense_output": "dense_output" in _log_opts,
        "hide_prefix": "hide_prefix" in _log_opts,
        "add_channel": "add_channel" in _log_opts,
        "add_debug_fileref": "add_debug_fileref" in _log_opts,
        "prefix_own_line": "prefix_own_line" in _log_opts,
        "disable_dict_to_json": "disable_dict_to_json" in _log_opts,
        "pretty_print_json": "pretty_print_json" in _log_opts,
        "ts_use_full": "ts_use_full" in _log_opts,
        "ts_use_relative": "ts_use_relative" in _log_opts,
        "ts_use_epoch": "ts_use_epoch" in _log_opts,
    }

    # reset and init root app logger by name
    _reset_logging(root_name)
    _default_cli_handler = None
    _default_file_handler = None
    _default_logger = logging.getLogger(root_name)
    _default_logger.setLevel(level.upper() if isinstance(level, str) else level)

    # init cli handler and attach logger
    if _options["disable_terminal_log"]:
        # prevent python logging module basic config from outputting to terminal
        _default_logger.addHandler(logging.NullHandler())
    else:
        _default_cli_handler = CliLogHandler(err=_options["log_to_stderr"])
        _default_cli_handler.setFormatter(CliLogFormatter(**_options))
        _default_logger.addHandler(_default_cli_handler)

    # init file handler and attach logger when given filename
    if file_handler_kwargs.get("filename") is not None:
        kwargs = {
            **{"maxBytes": 10000000, "backupCount": 5, "encoding": "utf8"},
            **file_handler_kwargs,
        }
        _default_file_handler = RotatingFileHandler(**kwargs)  # type: ignore
        # make sure formatter does not stylize output
        _default_file_handler.setFormatter(
            CliLogFormatter(force_no_color=True, **_options)
        )
        _default_logger.addHandler(_default_file_handler)


def getCliLogger(name: Optional[str] = None) -> logging.Logger:
    """Primary entry point for module. Provides a ready-to-use logger object.
    Call ``configRootLogger`` prior to using to configure the returned root logger

    :param name: returns a child of the root logger instead of the root logger itself
    """
    # if configRootLogger has not yet been called, call it with defaults only
    if _default_logger is None:
        configRootLogger()

    # root logger
    logger = cast(logging.Logger, _default_logger)

    if name is not None:
        if name.startswith(logger.name):
            logger = logging.getLogger(name)
        else:
            logger = logger.getChild(name)

    return logger


class CliLogFormatter(logging.Formatter):
    """
    Formatter object that transforms a LogRecord into a str log line (usually)
    includes a click styled prefix
    """

    # click.style options by log level
    _lvl_fmts: dict = {
        "DEBUG": {"fg": "cyan", "bold": False},
        "INFO": {"fg": "green", "bold": False},
        "WARN": {"fg": "bright_yellow", "bold": False},
        "ERROR": {"fg": "red", "bold": True},
        "CRITICAL": {"fg": "white", "bold": True, "bg": "red"},
        "DEFAULT": {"fg": "white", "bold": False},
    }

    # click.style options for timestamps
    _ts_fmts: dict = {"DEFAULT": {"fg": "white", "dim": True}}

    def __init__(
        self,
        fmt=None,
        datefmt=None,
        style="%",
        validate=True,
        force_no_color: bool = False,
        **kwargs,
    ):
        """Default Formatter params, along with output option flags:
        :param force_no_color: <internal flag> override click context color settings and
                               force stylized output OFF, useful when logging to file
                               or when logging should ignore styled output altogether
        :param kwargs: output option flags, expected to be bool values
        """
        super(CliLogFormatter, self).__init__(
            fmt=fmt, datefmt=datefmt, style=style, validate=validate
        )
        self.force_no_color = force_no_color

        # output option flags
        self.dense_output: bool = kwargs.get("dense_output", False)
        self.hide_prefix: bool = kwargs.get("hide_prefix", False)
        self.add_debug_fileref: bool = kwargs.get("add_debug_fileref", False)
        self.add_channel: bool = kwargs.get("add_channel", False)
        self.prefix_own_line: bool = kwargs.get("prefix_own_line", False)
        self.disable_dict_to_json: bool = kwargs.get("disable_dict_to_json", False)
        self.pretty_print_json: bool = kwargs.get("pretty_print_json", False)
        self.ts_use_full: bool = kwargs.get("ts_use_full", False)
        self.ts_use_relative: bool = kwargs.get("ts_use_relative", False)
        self.ts_use_epoch: bool = kwargs.get("ts_use_epoch", False)

        # assumes cwd at init is constant
        self.cwd = Path.cwd()

    def format(self, record: logging.LogRecord):
        """Overrides ``Formatter.format``

        uses the following options to modify output:
         * dense_output: add prefix to every record.msg line
         * hide_prefix: prevent generation of prefix blocks
         * prefix_own_line: adds a newline after prefix
        """
        msg: Union[str, list[str]] = self._msg(record)

        # when an empty string is logged, _msg returns an empty array
        # need to to seed with an empty string for downstream functions
        # to work as expected
        if len(msg) == 0:
            msg = [""]

        if self.hide_prefix:
            return "\n".join(msg)

        # generate prefix
        prefix = self._prefix(record)

        # apply prefix to every output line
        if self.dense_output:
            return "\n".join([f"{prefix}{msg_line}" for msg_line in msg])

        msg = "\n".join(msg)
        if self.prefix_own_line:
            return f"{prefix}\n{msg}"
        return f"{prefix}{msg}"

    def _block(self, value: str, fmt: dict) -> str:
        """Generate an individual prefix block of format "[ value ]"

        uses the following options to modify output:
         * force_no_color: output block as is, does not use ``click.style``
        """
        if self.force_no_color:
            return "".join(["[ ", value, " ]"])

        return "".join(["[ ", click.style(value, **fmt), " ]"])

    def _prefix(self, record: logging.LogRecord) -> str:
        """Creates styled prefix with the following blocks:

            [ LEVEL ][ TIMESTAMP ][ CHANNEL (optional) ][ FILEREF (optional) ]

        TIMESTAMP has default format of "%Y-%m-%d %H:%M:%S"

        uses the following options to modify output:
         * ts_use_ms: formats timestamp from record.created as millis since epoch
         * ts_use_relative: formats timestamp from record.relativeCreated as millis
                            since application startup
         * ts_use_full: formats default timestamp with ".%f" appended
         * add_channel: adds the logging channel prefix block
         * add_debug_fileref: adds a prefix block with filename and line number
        """
        # normalize level name
        lvl = record.levelname.upper()
        if lvl == "WARNING":
            lvl = "WARN"

        # current level format options
        lvl_fmt = self._lvl_fmts.get(lvl, self._lvl_fmts["DEFAULT"])

        if self.ts_use_epoch:
            ts = f"{int(record.created * 1000)}"
        elif self.ts_use_relative:
            ts = f"{record.relativeCreated:0.3f} ms"
        else:
            ts_output = _default_timestamp_format
            if self.ts_use_full:
                ts_output = ts_output + ".%f"
            ts = f"{datetime.fromtimestamp(record.created).strftime(ts_output)[:23]}"

        # construct level and timestamp
        line: list[str] = []
        line.append(self._block(f"{lvl:>5}", lvl_fmt))
        line.append(self._block(f"{ts}", self._ts_fmts["DEFAULT"]))

        # add channel name to prefix
        if self.add_channel:
            line.append(self._block(f"{record.name}", self._ts_fmts["DEFAULT"]))

        # add extra info to debug log lines
        if lvl == "DEBUG" and self.add_debug_fileref:
            try:
                pathname = str(Path(record.pathname).relative_to(self.cwd))
            except ValueError:
                pathname = record.pathname

            # show full time precision on debug lines
            line.append(self._block(f'"{pathname}", line {record.lineno}', lvl_fmt))

        # log message after a single space buffer
        line.append(" ")

        return "".join(line)

    def _msg(self, record: logging.LogRecord) -> list[str]:
        """Parses lines from the LogRecord object as a list of lines.

        If record.msg is a dict object, it is parsed into a json string by default.
        Additionally a valid traceback from record.exc_info is appended to output.

        uses the following options to modify output:
         * disable_dict_to_json:
         * pretty_print_json:
        """
        line: list[str] = []
        # handle different logged msg types
        if isinstance(record.msg, dict) and not self.disable_dict_to_json:
            if self.pretty_print_json:
                line.append(json.dumps(record.msg, default=lambda o: str(o), indent=4))
            else:
                # allow logging calls to modify how json.dumps operate by supplying
                # kwargs dict to `extra` param. see docs for more on `extra` param
                # https://docs.python.org/3/library/logging.html#logging.debug
                kwargs = record.__dict__.get("kwargs", {})
                if not isinstance(kwargs, dict):
                    kwargs = {}
                line.append(
                    json.dumps(
                        record.msg,
                        **{"default": lambda o: str(o), "indent": None, **kwargs},
                    )
                )
        else:
            line.append(record.getMessage())

        # add exception traceback if found, start on new line
        if record.exc_info:
            line.append("\n")
            line.append(self.formatException(record.exc_info))

        return "".join(line).splitlines()


class CliLogHandler(logging.Handler):
    """Uses ``click.echo`` to log messages to terminal

    Allows styled text to be controlled using the click ``Context.color``
    attribute. Additionally, click automatically manages styled text through
    piped output
    """

    def __init__(self, level=logging.NOTSET, err: bool = False):
        super(CliLogHandler, self).__init__(level)
        self.err = err

    def emit(self, record: logging.LogRecord):
        try:
            click.echo(self.format(record), err=self.err)
        except Exception:
            # prints logging exception traceback and continues
            self.handleError(record)
