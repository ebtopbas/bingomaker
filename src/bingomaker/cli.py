import argparse
import sys
from pathlib import Path

from . import __version__
from .config import BingoConfig, safe_path_component
from .generator import BingoBoardGenerator
from .visualizer import BingoBoardPdf


def _run_generate(args: argparse.Namespace) -> None:
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

    board_dir = args.output / safe_path_component(config.name)

    for name, board in zip(config.people, boards, strict=True):
        output_path = board_dir / f"{safe_path_component(name)}.pdf"

        renderer.render(
            board=board,
            name=name,
            output_path=output_path,
        )
        print(f"Wrote {output_path}")

    print(f"Generated {len(config.people)} board(s) in {board_dir}")


def _run_tui(args: argparse.Namespace) -> None:
    from .tui.app import BingoMakerApp

    BingoMakerApp(config_path=args.config).run()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bingomaker",
        description="Generate personalized Bingo boards as PDFs.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.set_defaults(
        func=_run_generate, config=None, output=Path("output"), seed=None
    )

    subparsers = parser.add_subparsers(dest="command", metavar="{generate,tui}")

    generate = subparsers.add_parser(
        "generate",
        help="Generate Bingo board PDFs from a config (default command).",
        description="Generate Bingo board PDFs from a config.",
    )
    generate.add_argument(
        "--config",
        type=Path,
        help="Path to the Bingo JSON configuration.",
    )
    generate.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Directory to write generated PDFs to (default: ./output).",
    )
    generate.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible board generation.",
    )
    generate.set_defaults(func=_run_generate)

    tui = subparsers.add_parser(
        "tui",
        help="Launch the interactive Bingo board builder.",
        description="Launch the interactive Bingo board builder.",
    )
    tui.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a Bingo JSON configuration to load on startup.",
    )
    tui.set_defaults(func=_run_tui)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        args.func(args)
    except (ValueError, TypeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
