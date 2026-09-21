"""Compare an always-on prompt with a two-cycle skill-loading loop."""

import json
from time import perf_counter
from typing import Any

from catalog import catalog_prompt, load_skill


BASE_INSTRUCTIONS = """You are a B2B marketing assistant. When writing the final
campaign, create every asset requested in the brief. Use only facts in the
brief. Do not invent performance numbers, customers, endorsements, or
guarantees. Return the campaign copy with clear section headings."""

SKILL_TOOL = {
    "type": "function",
    "name": "load_skill",
    "description": "Load detailed instructions for a relevant marketing skill.",
    "parameters": {
        "type": "object",
        "properties": {"skill_name": {"type": "string"}},
        "required": ["skill_name"],
        "additionalProperties": False,
    },
}


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
    """Return the short catalog and instructions for the selection cycle."""
    catalog_text = catalog_prompt(catalog)
    selection_instructions = (
        BASE_INSTRUCTIONS
        + "\n\nFirst select every skill relevant to the requested assets. Call "
        "load_skill for all of them in this cycle. Do not write the campaign "
        "yet. The available names and routing descriptions are:\n"
        + catalog_text
    )
    return catalog_text, selection_instructions


def resolve_skill_call(item: Any, catalog: dict) -> tuple[dict, dict]:
    """Validate one requested skill and build its Responses API tool result."""
    name = "(invalid)"
    try:
        if item.name != "load_skill":
            raise ValueError(f"Unsupported tool: {item.name}")
        arguments = json.loads(item.arguments)
        name = arguments["skill_name"]
        if not isinstance(name, str):
            raise ValueError("skill_name must be a string")
        skill_text, path = load_skill(name, catalog)
        result = skill_text
        loaded = True
    except (ValueError, KeyError, TypeError) as error:
        path = None
        result = f"ERROR: {error}"
        loaded = False
    skill_call = {
        "skill": name,
        "loaded": loaded,
        "path": str(path) if path else None,
        "chars": len(result) if loaded else 0,
    }
    tool_output = {"type": "function_call_output", "call_id": item.call_id, "output": result}
    return skill_call, tool_output


def write_with_skills(
    client: Any, model: str, selection: Any, tool_outputs: list[dict]
) -> tuple[Any, float]:
    """Continue from selection and write with the returned skill instructions."""
    writing_input: Any = tool_outputs or "Write the requested campaign now. No skill was loaded."
    return call_model(
        client,
        model=model,
        instructions=BASE_INSTRUCTIONS + "\nUse the skill instructions loaded in the previous cycle.",
        previous_response_id=selection.id,
        input=writing_input,
    )


def run_with_skills(client: Any, model: str, brief: str, catalog: dict) -> dict:
    """Select skills in cycle 1, then write with loaded guidance in cycle 2."""
    catalog_text, selection_instructions = build_selection_instructions(catalog)
    print("\n--- SKILLS CYCLE 1 OF 2: SELECT AND LOAD ---")
    print(f"Prompt includes skill names and short descriptions only ({len(catalog_text)} catalog characters).")
    selection, selection_seconds = call_model(
        client,
        model=model,
        instructions=selection_instructions,
        input=brief,
        tools=[SKILL_TOOL],
    )

    skill_calls = []
    tool_outputs = []
    for item in selection.output:
        if item.type != "function_call":
            continue
        skill_call, tool_output = resolve_skill_call(item, catalog)
        skill_calls.append(skill_call)
        tool_outputs.append(tool_output)
        print(f"AGENT TOOL CALL: {item.name}({skill_call['skill']})")
        print(f"TOOL RESULT: {'loaded ' + skill_call['path'] if skill_call['loaded'] else tool_output['output']}")

    if not tool_outputs:
        print("No skill was requested in the selection cycle.")
    full_skill_chars = sum(call["chars"] for call in skill_calls if call["loaded"])
    print(f"Full skill text supplied through tool results: {full_skill_chars} characters.")
    pause_after_cycle()

    print("\n--- SKILLS CYCLE 2 OF 2: WRITE CAMPAIGN ---")
    final, writing_seconds = write_with_skills(client, model, selection, tool_outputs)
    final_text = final.output_text.strip()
    print("FINAL CAMPAIGN:\n" + (final_text or "(empty response)"))
    pause_after_cycle()

    input_tokens, output_tokens, total_tokens = token_totals([selection, final])
    return {
        "mode": "skills",
        "status": "complete" if final_text else "empty_response",
        "output": final_text,
        "cycles": 2,
        "loaded_skills": list(dict.fromkeys(call["skill"] for call in skill_calls if call["loaded"])),
        "skill_calls": skill_calls,
        "prompt_chars": len(selection_instructions) + len(brief),
        "skill_chars_in_prompt": 0,
        "full_skill_chars": full_skill_chars,
        "elapsed_seconds": round(selection_seconds + writing_seconds, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def run_agent(client: Any, model: str, brief: str, mode: str, catalog: dict) -> dict:
    if mode == "basic":
        return run_basic(client, model, brief, catalog)
    if mode == "skills":
        return run_with_skills(client, model, brief, catalog)
    raise ValueError(f"Unknown mode: {mode}")
