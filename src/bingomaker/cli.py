import argparse
from pathlib import Path

from .config import BingoConfig
from .generator import BingoBoardGenerator
from .visualizer import BingoBoardPdf


def _safe_path_component(value: str) -> str:
    return value.replace("/", "-").replace("\\", "-")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Bingo boards as PDFs.")

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to the Bingo JSON configuration.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Directory to write generated PDFs to (default: ./output).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible board generation.",
    )

    args = parser.parse_args(argv)

    if args.config is None:
        config = BingoConfig(
            "test",
            "FREE SPACE",
            [f"sentence_{i}" for i in range(8)],
            ["Alice", "Bob", "Charlie"],
        )
    else:
        config = BingoConfig.from_json(args.config)

    generator = BingoBoardGenerator(config, seed=args.seed)
    renderer = BingoBoardPdf(config.name, config.free_space is not None)

    boards = generator.generate(len(config.people))

    for name, board in zip(config.people, boards):
        output_path = (
            args.output
            / _safe_path_component(config.name)
            / f"{_safe_path_component(name)}.pdf"
        )

        renderer.render(
            board=board,
            name=name,
            output_path=output_path,
        )
