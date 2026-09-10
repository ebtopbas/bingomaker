# bingomaker

Generate personalized bingo boards as PDFs. Give it a list of sentences and a
list of people, and it shuffles a unique board per person and renders each as
a printable PDF.

## Requirements

- Python 3.13+

## Setup

```sh
git clone https://github.com/canonhead/bingomaker.git
cd bingomaker
```

This project uses [uv](https://docs.astral.sh/uv/) for dependency management
(it's not required to run bingomaker — a regular venv + `pip install .` works
too — but the commands below assume it):

```sh
uv sync
```

## Usage

```sh
uv run bingomaker --config path/to/config.json
```

Options:

| Flag       | Description                                              | Default   |
| ---------- | ---------------------------------------------------------| --------- |
| `--config` | Path to a JSON config (see below). Omit for a demo board.| —         |
| `--output` | Directory to write generated PDFs to.                    | `output`  |
| `--seed`   | Random seed, for reproducible board generation.          | —         |

PDFs are written to `<output>/<name>/<person>.pdf` for each person in the
config.

## Config format

```json
{
    "name": "Office Bingo",
    "free_space": "Free space",
    "sentences": [
        "Someone joins the call late",
        "Meeting runs over time",
        "..."
    ],
    "people": ["Alice", "Bob", "Charlie"]
}
```

- **`name`** — board title, also used as the output subfolder.
- **`free_space`** — text for a free center cell. Optional: omit the key (or
  set it to `null`) to generate a board with no free space.
- **`sentences`** — the pool of cell contents. Must all be unique, and must
  not include the `free_space` text.
- **`people`** — one board is generated per person. Names must be unique.

### Board size

Boards are always square. The number of sentences determines the side
length:

- **With `free_space`**: sentences must number `side² - 1` for an odd side
  — e.g. 8, 24, 48, or 80 sentences for a 3×3, 5×5, 7×7, or 9×9 board.
- **Without `free_space`**: sentences must number a perfect square — e.g.
  9, 16, or 25 sentences for a 3×3, 4×4, or 5×5 board.

If the sentence count doesn't fit, `bingomaker` raises a clear error telling
you what counts are valid.

## Development

```sh
uv run ruff check --fix .   # lint (includes import sorting)
uv run ruff format .        # format
uv run ty check             # type check
```
