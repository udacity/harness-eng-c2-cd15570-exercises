"""Interactive pause boundaries for the classroom demo."""


def pause_after_loop_start(mode: str) -> None:
    input(f"\n{mode.upper()} loop ready. Press Return to start cycle 1...")


def pause_after_cycle() -> None:
    input("\nCycle complete. Press Return to continue...")
