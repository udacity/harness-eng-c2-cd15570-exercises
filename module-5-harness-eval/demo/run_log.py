"""Copy terminal output to a timestamped demo log."""

import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Iterator, TextIO


class Tee:
    def __init__(self, screen: TextIO, target: TextIO) -> None:
        self.screen = screen
        self.target = target

    def write(self, message: str) -> int:
        self.screen.write(message)
        self.target.write(message)
        self.screen.flush()
        self.target.flush()
        return len(message)

    def flush(self) -> None:
        self.screen.flush()
        self.target.flush()


@contextmanager
def tee_run_output(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as target:
        with redirect_stdout(Tee(sys.stdout, target)):
            with redirect_stderr(Tee(sys.stderr, target)):
                yield
