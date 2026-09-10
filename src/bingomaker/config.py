from __future__ import annotations

import json
import math
from pathlib import Path


class BingoConfig:
    name: str
    free_space: str
    sentences: list[str]
    people: list[str]

    def __init__(
        self, name: str, free_space: str, sentences: list[str], people: list[str]
    ):
        self.name = name
        self.free_space = free_space
        self.sentences = sentences
        self.people = people

        _ = self.dimensions

    @classmethod
    def from_json(cls, path: Path) -> BingoConfig:
        with path.open(encoding="utf-8") as fp:
            config = json.load(fp)

        return cls(
            name=config["name"],
            free_space=config["free_space"],
            sentences=config["sentences"],
            people=config["people"],
        )

    @property
    def dimensions(self) -> tuple[int, int]:
        n_cells = len(self.sentences) + 1

        side = math.isqrt(n_cells)

        if side * side != n_cells or side % 2 == 0:
            raise ValueError(
                f"Cannot create a square board with a centered free space "
                f"from {len(self.sentences)} sentences. "
                f"The number of sentences must be side^2 - 1 for an odd side "
                f"(e.g. 8, 24, 48, 80 sentences for a 3x3, 5x5, 7x7, 9x9 board)."
            )

        return side, side
