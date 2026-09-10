import argparse
from pathlib import Path

from . import BingoBoardGenerator, BingoBoardPdf, BingoConfig

if __name__ == "__main__":
    OUTPUT_FOLDER = Path("output")

    parser = argparse.ArgumentParser(description="Generate Bingo boards as PDFs.")

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to the Bingo JSON configuration.",
    )

    args = parser.parse_args()

    if args.config is None:
        config = BingoConfig(
            "test",
            "FREE SPACE",
            [f"sentence_{i}" for i in range(8)],
            ["Alice", "Bob", "Charlie"],
        )
    else:
        config = BingoConfig.from_json(args.config)

    generator = BingoBoardGenerator(config)
    renderer = BingoBoardPdf(config.name, config.free_space is not None)

    boards = generator.generate(len(config.people))

    for name, board in zip(config.people, boards):
        output_path = OUTPUT_FOLDER / config.name / f"{name}.pdf"

        renderer.render(
            board=board,
            name=name,
            output_path=output_path,
        )
