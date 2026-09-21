"""Compare an always-on prompt with a two-cycle skill-loading loop."""

import json
from time import perf_counter
from typing import Any

from catalog import catalog_prompt, load_skill


BASE_INSTRUCTIONS = """You are a B2B marketing assistant. When writing the final
campaign, create every asset requested in the brief. Use only facts in the
brief. Do not invent performance numbers, customers, endorsements, or
guarantees. Return the campaign copy with clear section headings."""

# TODO: Define a Responses API function tool named load_skill. It should take
# one required string argument, skill_name, and reject additional properties.
# The model will see this tool only during the skill-selection cycle.
SKILL_TOOL: dict[str, Any] = {}


def pause_after_cycle() -> None:
    input("\nCycle complete. Press Return to continue...")


def call_model(client: Any, **kwargs: Any) -> tuple[Any, float]:
    """Measure model time without counting the student's pause."""
    started = perf_counter()
    response = client.responses.create(**kwargs)
    return response, perf_counter() - started


def token_totals(responses: list[Any]) -> tuple[int | None, int | None, int | None]:
    """Sum API usage for a run; report unavailable when usage is missing."""
    counts = []
    for response in responses:
        usage = getattr(response, "usage", None)
        input_count = getattr(usage, "input_tokens", None)
        output_count = getattr(usage, "output_tokens", None)
        if input_count is None or output_count is None:
            return None, None, None
        counts.append((input_count, output_count))
    input_tokens = sum(count[0] for count in counts)
    output_tokens = sum(count[1] for count in counts)
    return input_tokens, output_tokens, input_tokens + output_tokens


def run_basic(client: Any, model: str, brief: str, catalog: dict) -> dict:
    """Send every full SKILL.md to the model in one always-on prompt."""
    skill_texts = [load_skill(name, catalog)[0] for name in catalog]
    all_skill_text = "\n\n".join(skill_texts)
    full_skill_chars = sum(len(skill_text) for skill_text in skill_texts)
    instructions = BASE_INSTRUCTIONS + "\n\nMARKETING GUIDANCE\n" + all_skill_text
    print("\n--- BASIC CYCLE 1 OF 1 ---")
    print(f"Prompt includes all {len(catalog)} complete SKILL.md files: {', '.join(catalog)}.")
    print(f"Full skill text supplied: {full_skill_chars} characters.")

    response, seconds = call_model(client, model=model, instructions=instructions, input=brief)
    final_text = response.output_text.strip()
    print("FINAL CAMPAIGN:\n" + (final_text or "(empty response)"))
    pause_after_cycle()
    input_tokens, output_tokens, total_tokens = token_totals([response])
    return {
        "mode": "basic",
        "status": "complete" if final_text else "empty_response",
        "output": final_text,
        "cycles": 1,
        "loaded_skills": [],
        "skill_calls": [],
        "prompt_chars": len(instructions) + len(brief),
        "skill_chars_in_prompt": len(all_skill_text),
        "full_skill_chars": full_skill_chars,
        "elapsed_seconds": round(seconds, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def build_selection_instructions(catalog: dict) -> tuple[str, str]:
    """Return (short catalog text, selection instructions).

    TODO: Call catalog_prompt and combine its result with BASE_INSTRUCTIONS.
    Ask the model to request every relevant skill before it writes. The full
    text of a SKILL.md file must not appear in this initial prompt.
    """
    raise NotImplementedError("Build the skill-selection instructions.")


def resolve_skill_call(item: Any, catalog: dict) -> tuple[dict, dict]:
    """Return (skill call record, function_call_output) for one tool call.

    TODO: Accept only load_skill, parse item.arguments as JSON, require a
    string skill_name, and call the supplied load_skill function. For a valid
    name, return the full skill text as the tool output and record its path
    and character count. For malformed arguments or an unknown name, return
    an ERROR tool output with the same item.call_id; do not read any other
    file. The call record should contain skill, loaded, path, and chars.
    """
    raise NotImplementedError("Resolve a requested skill safely.")


def write_with_skills(
    client: Any, model: str, selection: Any, tool_outputs: list[dict]
) -> tuple[Any, float]:
    """Return the final model response and model seconds for cycle 2.

    TODO: Continue from selection.id using previous_response_id. Send the
    function_call_output items as input and do not offer tools in this call.
    When tool_outputs is empty, still ask for a final campaign. Use call_model
    so the timing excludes the student's pause.
    """
    raise NotImplementedError("Write the campaign with loaded skills.")


def run_with_skills(client: Any, model: str, brief: str, catalog: dict) -> dict:
    """Run selection, tool loading, and writing as two visible model cycles.

    TODO: Use the helpers above to:
    1. Call the model with selection instructions, the brief, and SKILL_TOOL.
    2. Resolve each function call in selection.output, print the result, and
       collect skill records and tool outputs. Ignore non-tool output items.
       Print a no-skill message when appropriate and pause after cycle 1.
    3. Call write_with_skills, print the campaign, and pause after cycle 2.
    4. Sum input and output tokens from both responses with token_totals.
       Return the same result keys as run_basic. Count only successfully
       loaded full skill text in full_skill_chars and list each loaded skill
       once in loaded_skills. The comparison table needs these fields.
    """
    raise NotImplementedError("Implement the two-cycle skill-loading run.")


def run_agent(client: Any, model: str, brief: str, mode: str, catalog: dict) -> dict:
    if mode == "basic":
        return run_basic(client, model, brief, catalog)
    if mode == "skills":
        return run_with_skills(client, model, brief, catalog)
    raise ValueError(f"Unknown mode: {mode}")
