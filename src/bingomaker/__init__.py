from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("bingomaker")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .cli import main
from .config import BingoConfig
from .generator import BingoBoardGenerator
from .visualizer import BingoBoardPdf

__all__ = [
    "BingoBoardGenerator",
    "BingoBoardPdf",
    "BingoConfig",
    "__version__",
    "main",
]
