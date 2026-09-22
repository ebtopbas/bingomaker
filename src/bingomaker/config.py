from __future__ import annotations

import json
import math
from pathlib import Path


def safe_path_component(value: str) -> str:
    """Sanitize a name for use as a single path component (no separators)."""
    return value.replace("/", "-").replace("\\", "-")


class BingoConfig:
    name: str
    free_space: str | None
    sentences: list[str]
    people: list[str]

    def __init__(
        self,
        name: str,
        free_space: str | None,
        sentences: list[str],
        people: list[str],
    ):
        if not name:
            raise ValueError("name must not be empty")

        if free_space is not None and not free_space:
            raise ValueError("free_space must not be empty; use None to omit it")

        if not sentences:
            raise ValueError("sentences must not be empty")

        if len(sentences) != len(set(sentences)):
            raise ValueError("sentences must not contain duplicates")

        if free_space is not None and free_space in sentences:
            raise ValueError(
                "free_space must not also appear in sentences, "
                "otherwise that sentence's cell would be styled as the free space"
            )

        if not people:
            raise ValueError("people must not be empty")

        if len(people) != len(set(people)):
            raise ValueError(
                "people must not contain duplicates, "
                "otherwise their boards would overwrite each other's output file"
            )

        self.name = name
        self.free_space = free_space
        self.sentences = sentences
        self.people = people

        _ = self.dimensions

    @classmethod
    def from_json(cls, path: Path) -> BingoConfig:
        with path.open(encoding="utf-8") as fp:
            config = json.load(fp)

        required_keys = {"name", "sentences", "people"}
        missing_keys = required_keys - config.keys()

        if missing_keys:
            raise ValueError(
                f"Config at {path} is missing required key(s): "
                f"{', '.join(sorted(missing_keys))}"
            )

        name = config["name"]
        free_space = config.get("free_space")
        sentences = config["sentences"]
        people = config["people"]

        if not isinstance(name, str):
            raise TypeError(f"Config at {path}: 'name' must be a string")

        if free_space is not None and not isinstance(free_space, str):
            raise TypeError(f"Config at {path}: 'free_space' must be a string or null")

        if not isinstance(sentences, list) or not all(
            isinstance(s, str) for s in sentences
        ):
            raise TypeError(f"Config at {path}: 'sentences' must be a list of strings")

        if not isinstance(people, list) or not all(isinstance(p, str) for p in people):
            raise TypeError(f"Config at {path}: 'people' must be a list of strings")

        return cls(
            name=name,
            free_space=free_space,
            sentences=sentences,
            people=people,
        )

    @property
    def dimensions(self) -> tuple[int, int]:
        has_free_space = self.free_space is not None
        n_cells = len(self.sentences) + (1 if has_free_space else 0)

        side = math.isqrt(n_cells)

        if side * side != n_cells:
            if has_free_space:
                raise ValueError(
                    f"Cannot create a square board with a centered free space "
                    f"from {len(self.sentences)} sentences. "
                    f"The number of sentences must be side^2 - 1 for some side "
                    f"(e.g. 8, 24, 48 sentences for a 3x3, 5x5, 7x7 board)."
                )

            raise ValueError(
                f"Cannot create a square board from {len(self.sentences)} sentences. "
                f"The number of sentences must be a perfect square "
                f"(e.g. 9, 16, 25 sentences for a 3x3, 4x4, 5x5 board)."
            )

        if has_free_space and side % 2 == 0:
            raise ValueError(
                f"Cannot center a free space on a board with an even side "
                f"({side}). Use side^2 - 1 sentences for an odd side, "
                f"or omit free_space."
            )

        return side, side
