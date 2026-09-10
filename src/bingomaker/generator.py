import math

import numpy as np

from .config import BingoConfig


class BingoBoardGenerator:
    def __init__(self, config: BingoConfig, seed: int | None = None):
        self.config = config
        self.rng = np.random.default_rng(seed)

    def generate(self, n: int) -> list[np.ndarray]:
        if n < 1:
            raise ValueError("n must be at least 1")

        max_boards = math.factorial(len(self.config.sentences))

        if n > max_boards:
            raise ValueError(
                f"Cannot generate {n} unique boards. "
                f"There are only {max_boards} possible arrangements."
            )

        boards = []
        seen: set[tuple[str, ...]] = set()

        while len(boards) < n:
            sentences = self.config.sentences.copy()
            self.rng.shuffle(sentences)

            key = tuple(sentences)

            if key in seen:
                continue

            seen.add(key)
            boards.append(self._create_board(sentences))

        return boards

    def _create_board(self, sentences: list[str]) -> np.ndarray:
        rows, cols = self.config.dimensions

        board = np.empty((rows, cols), dtype=object)

        sentence_iter = iter(sentences)

        free_cell = (
            (rows // 2, cols // 2) if self.config.free_space is not None else None
        )

        for row in range(rows):
            for col in range(cols):
                if (row, col) == free_cell:
                    board[row, col] = self.config.free_space
                else:
                    board[row, col] = next(sentence_iter)

        return board
