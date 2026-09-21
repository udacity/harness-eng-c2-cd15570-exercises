"""Run a campaign with all skills in the prompt or with skills loaded on demand."""

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from agent import run_agent
from catalog import discover_skills
from run_log import tee_run_output


BASE_DIR = Path(__file__).resolve().parent
CAMPAIGNS_DIR = BASE_DIR / "campaigns"
SKILLS_DIR = BASE_DIR / "skills"
OUTPUT_DIR = BASE_DIR / "output"
BASE_URL = "https://openai.vocareum.com/v1"


def parse_args() -> argparse.Namespace:
    names = sorted(path.stem for path in CAMPAIGNS_DIR.glob("*.txt"))
    parser = argparse.ArgumentParser(description="Compare always-on instructions with on-demand skills.")
    parser.add_argument("mode", nargs="?", choices=("basic", "skills", "compare"), default="compare")
    parser.add_argument("--campaign", choices=(*names, "all"), help="Campaign file; defaults to inspectai_campaign.")
    parser.add_argument("--brief-file", type=Path, help="Use your own UTF-8 campaign brief.")
    args = parser.parse_args()
    if args.brief_file and args.campaign:
        parser.error("choose either --campaign or --brief-file")
    if args.brief_file and not args.brief_file.is_file():
        parser.error(f"brief file does not exist: {args.brief_file}")
    return args


def print_comparison(rows: list[dict]) -> None:
    columns = (20, 8, 16, 7, 7, 7, 13)

    def format_row(campaign: str, mode: str, values: tuple, skills: str) -> str:
        cells = (campaign, mode, *values)
        formatted = " | ".join(f"{str(cell):<{width}}" for cell, width in zip(cells, columns))
        return f"{formatted} | {skills}"

    def percent_change(basic: int | float | None, skills: int | float | None) -> str:
        if basic is None or skills is None or basic == 0:
            return "n/a"
        change = (skills - basic) / basic * 100
        return "0.0%" if change == 0 else f"{change:+.1f}%"

    print("\n================ CONTEXT, TOKEN, AND LATENCY COMPARISON ================")
    headers = ("Full skill chars", "Input", "Output", "Total", "Model seconds")
    print(format_row("Campaign", "Mode", headers, "Skills loaded"))
    print("-+-".join("-" * width for width in columns) + "-+----------------")
    basic_by_campaign = {row["campaign"]: row["run"] for row in rows if row["run"]["mode"] == "basic"}
    for row in rows:
        run = row["run"]
        skills_label = (
            "(all in prompt)" if run["mode"] == "basic"
            else ", ".join(run["loaded_skills"]) or "(none)"
        )
        metrics = (
            run["full_skill_chars"], run["input_tokens"], run["output_tokens"],
            run["total_tokens"], run["elapsed_seconds"],
        )
        print(format_row(row["campaign"], run["mode"], metrics, skills_label))
        if run["mode"] == "skills" and row["campaign"] in basic_by_campaign:
            basic = basic_by_campaign[row["campaign"]]
            keys = ("full_skill_chars", "input_tokens", "output_tokens", "total_tokens", "elapsed_seconds")
            changes = tuple(percent_change(basic[key], run[key]) for key in keys)
            print(format_row(row["campaign"], "change", changes, "(skills vs basic)"))
    print("Change % = 100 × (skills - basic) / basic; negative means less, positive means more.")
    print("Full skill chars count SKILL.md text sent in the prompt or returned by load_skill; they are not API tokens.")
    print("Token counts come from API usage; model seconds exclude time waiting for Return.")


def main() -> None:
    args = parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.mode}-{stamp}.log"

    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        load_dotenv(BASE_DIR / ".env")
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not key:
            raise SystemExit(f"Set OPENAI_API_KEY in {BASE_DIR / '.env'} first.")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        client = OpenAI(base_url=BASE_URL, api_key=key)
        catalog = discover_skills(SKILLS_DIR)

        if args.brief_file:
            campaigns = [args.brief_file]
        elif args.campaign == "all":
            campaigns = sorted(CAMPAIGNS_DIR.glob("*.txt"))
        else:
            campaigns = [CAMPAIGNS_DIR / f"{args.campaign or 'inspectai_campaign'}.txt"]
        modes = ("basic", "skills") if args.mode == "compare" else (args.mode,)

        print("\nMARKETING SKILLS HARNESS")
        print(f"Model: {model} | Campaigns: {len(campaigns)} | Mode: {args.mode}")
        print(f"Skills available: {', '.join(catalog)}")
        rows = []
        for path in campaigns:
            brief = path.read_text(encoding="utf-8").strip()
            print(f"\n================ CAMPAIGN: {path.stem} ================")
            print("BRIEF:\n" + brief)
            for mode in modes:
                run = run_agent(client, model, brief, mode, catalog)
                print(
                    f"{mode.upper()} METRICS: {run['input_tokens']} input + "
                    f"{run['output_tokens']} output = {run['total_tokens']} total tokens; "
                    f"{run['elapsed_seconds']} model seconds."
                )
                rows.append({"campaign": path.stem, "run": run})

        print_comparison(rows)


if __name__ == "__main__":
    main()
