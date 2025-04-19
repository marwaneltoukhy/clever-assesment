from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from rich.theme import Theme
import logging

# Define a custom theme
custom_theme = Theme(
    {
        "info": "dim cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "progress.description": "cyan",
        "progress.percentage": "green",
        "progress.remaining": "yellow",
    }
)

# Create a console instance with the custom theme
console = Console(theme=custom_theme)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)

# Create a logger instance
logger = logging.getLogger("data_analyzer")


def create_progress() -> Progress:
    """Create a progress bar with custom styling."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def print_header(text: str) -> None:
    """Print a styled header panel."""
    console.print(Panel.fit(text, style="bold blue", border_style="blue"))


def print_success(text: str) -> None:
    """Print a success message."""
    console.print(f"[success]✓ {text}[/success]")


def print_error(text: str) -> None:
    """Print an error message."""
    console.print(f"[error]✗ {text}[/error]")


def print_warning(text: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]⚠ {text}[/warning]")


def print_info(text: str) -> None:
    """Print an info message."""
    console.print(f"[info]ℹ {text}[/info]")
