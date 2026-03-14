# This logger is based on Loggity (https://github.com/slpuk/loggity)
# Licensed under MIT License
# Author: slpuk

"""Simple, dependency-free logger with colors"""


class Colors:
    """ANSI color codes for terminal output.

    These constants provide consistent color definitions across all loggers.
    Colors are only applied when colored output is enabled.
    """

    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class Logger:
    """Simple, beautiful logger with optional colors.

    Provides standard logging levels (INFO, WARN, ERROR, DEBUG, SUCCESS).
    """

    _default_colors = {
        "INFO": Colors.BLUE,
        "WARN": Colors.YELLOW,
        "ERROR": Colors.RED,
        "DEBUG": Colors.WHITE,
        "SUCCESS": Colors.GREEN,
    }

    def __init__(self):
        """Initialize logger with given configuration."""

    def _log(self, header: str, color: str, message: str) -> None:
        """Internal method for unified logging logic.

        This method centralizes all logging to ensure consistency between
        console output and file writing.

        Args:
            header: Log level or custom header.
            color: ANSI color code for the header.
            message: Log message content.
        """
        print(f"{color}{header}{Colors.RESET}:   \t{message}")

    def info(self, message: str) -> None:
        """Log informational message (blue)."""
        self._log("INFO", self._default_colors["INFO"], message)

    def warn(self, message: str) -> None:
        """Log warning message (yellow)."""
        self._log("WARN", self._default_colors["WARN"], message)

    def error(self, message: str) -> None:
        """Log error message (red)."""
        self._log("ERROR", self._default_colors["ERROR"], message)

    def debug(self, message: str) -> None:
        """Log debug message (white)."""
        self._log("DEBUG", self._default_colors["DEBUG"], message)

    def success(self, message: str) -> None:
        """Log success message (green)."""
        self._log("SUCCESS", self._default_colors["SUCCESS"], message)

    def custom(self, header: str, color: str, message: str) -> None:
        """Log with custom header and color.
        
        Args:
            header: Custom header text (e.g., "METRIC", "AUDIT").
            color: Any color from Colors class.
            message: Log message content.
        """
        self._log(header, color, message)