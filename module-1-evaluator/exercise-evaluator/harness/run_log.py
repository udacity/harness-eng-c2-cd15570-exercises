import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Iterator, TextIO


class Tee:
    def __init__(self, screen: TextIO, log_file: TextIO) -> None:
        self.screen = screen
        self.log_file = log_file

    def write(self, message: str) -> int:
        self.screen.write(message)
        self.log_file.write(message)
        self.screen.flush()
        self.log_file.flush()
        return len(message)

    def flush(self) -> None:
        self.screen.flush()
        self.log_file.flush()


@contextmanager
def tee_run_output(log_path: Path) -> Iterator[None]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("x", encoding="utf-8") as log_file:
        with redirect_stdout(Tee(sys.stdout, log_file)):
            with redirect_stderr(Tee(sys.stderr, log_file)):
                yield
