"""Compare eager skill context with a two-cycle on-demand skill loop."""

import json
from collections.abc import Callable
from time import perf_counter
from typing import Any

from catalog import catalog_prompt, load_skill


BASE_INSTRUCTIONS = """You are an incident-response assistant. Write exactly
60 whitespace-separated words. Include INC-2048. Use only authoritative facts,
distinguish evidence from hypotheses, do not claim an action or recovery that
has not occurred, and give a useful next step. Return only the requested note."""

SKILL_TOOL: dict[str, Any] = {
    "type": "function",
    "name": "load_skill",
    "description": "Load detailed instructions for one relevant incident-response skill.",
    "parameters": {
        "type": "object",
        "properties": {"skill_name": {"type": "string"}},
        "required": ["skill_name"],
        "additionalProperties": False,
    },
}


def call_model(client: Any, **kwargs: Any) -> tuple[Any, float]:
    """Measure model time without counting a presenter pause."""

    started = perf_counter()
    response = client.responses.create(**kwargs)
    return response, perf_counter() - started


def token_totals(responses: list[Any]) -> tuple[int | None, int | None, int | None]:
    counts: list[tuple[int, int]] = []
    for response in responses:
        usage = getattr(response, "usage", None)
        input_count = getattr(usage, "input_tokens", None)
        output_count = getattr(usage, "output_tokens", None)
        if input_count is None or output_count is None:
            return None, None, None
        counts.append((input_count, output_count))
    input_tokens = sum(item[0] for item in counts)
    output_tokens = sum(item[1] for item in counts)
    return input_tokens, output_tokens, input_tokens + output_tokens


def run_basic(
    client: Any,
    model: str,
    brief: str,
    catalog: dict,
    *,
    emit: Callable[[str], None] = print,
    pause: Callable[[], None] = lambda: None,
) -> dict:
    """Send every complete skill in one eager, always-on prompt."""

    skill_texts = [load_skill(name, catalog)[0] for name in catalog]
    all_skill_text = "\n\n".join(skill_texts)
    full_skill_chars = sum(len(text) for text in skill_texts)
    instructions = BASE_INSTRUCTIONS + "\n\nALL INCIDENT GUIDANCE\n" + all_skill_text
    emit("\n--- BASIC CYCLE 1 OF 1 ---")
    emit(
        f"Prompt includes all {len(catalog)} complete SKILL.md files: "
        f"{', '.join(catalog)}."
    )
    emit(f"Full skill text supplied: {full_skill_chars} characters.")
    response, seconds = call_model(
        client, model=model, instructions=instructions, input=brief
    )
    final_text = response.output_text.strip()
    emit("FINAL INCIDENT NOTE:\n" + (final_text or "(empty response)"))
    pause()
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
    """Build cycle-one instructions from names and descriptions only."""

    catalog_text = catalog_prompt(catalog)
    selection_instructions = (
        BASE_INSTRUCTIONS
        + "\n\nFirst request every skill relevant to this incident task. Call "
        "load_skill for all relevant skills in this cycle. Do not write the "
        "incident note yet. Available names and routing descriptions:\n"
        + catalog_text
    )
    return catalog_text, selection_instructions


def resolve_skill_call(item: Any, catalog: dict) -> tuple[dict, dict]:
    """Validate one request and return its record and tool result."""

    name = "(invalid)"
    try:
        if item.name != "load_skill":
            raise ValueError(f"Unsupported tool: {item.name}")
        arguments = json.loads(item.arguments)
        if not isinstance(arguments, dict) or set(arguments) != {"skill_name"}:
            raise ValueError("arguments must contain only skill_name")
        name = arguments["skill_name"]
        if not isinstance(name, str):
            raise ValueError("skill_name must be a string")
        skill_text, path = load_skill(name, catalog)
        result = skill_text
        loaded = True
    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as error:
        path = None
        result = f"ERROR: {error}"
        loaded = False
    record = {
        "skill": name,
        "loaded": loaded,
        "path": str(path) if path else None,
        "chars": len(result) if loaded else 0,
    }
    tool_output = {
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": result,
    }
    return record, tool_output


def write_with_skills(
    client: Any,
    model: str,
    selection: Any,
    tool_outputs: list[dict],
) -> tuple[Any, float]:
    """Continue from selection without offering the loading tool again."""

    writing_input: Any = tool_outputs or (
        "Write the requested incident note now. No skill was loaded."
    )
    return call_model(
        client,
        model=model,
        instructions=(
            BASE_INSTRUCTIONS
            + "\nUse the skill instructions returned in the previous cycle."
        ),
        previous_response_id=selection.id,
        input=writing_input,
    )


def run_with_skills(
    client: Any,
    model: str,
    brief: str,
    catalog: dict,
    *,
    emit: Callable[[str], None] = print,
    pause: Callable[[], None] = lambda: None,
) -> dict:
    """Select and load skills in cycle one, then write in cycle two."""

    catalog_text, selection_instructions = build_selection_instructions(catalog)
    emit("\n--- SKILLS CYCLE 1 OF 2: SELECT AND LOAD ---")
    emit(
        "Prompt includes skill names and descriptions only "
        f"({len(catalog_text)} catalog characters)."
    )
    selection, selection_seconds = call_model(
        client,
        model=model,
        instructions=selection_instructions,
        input=brief,
        tools=[SKILL_TOOL],
    )

    skill_calls: list[dict] = []
    tool_outputs: list[dict] = []
    for item in selection.output:
        if item.type != "function_call":
            continue
        record, tool_output = resolve_skill_call(item, catalog)
        skill_calls.append(record)
        tool_outputs.append(tool_output)
        emit(f"AGENT TOOL CALL: {item.name}({record['skill']})")
        result = "loaded " + record["path"] if record["loaded"] else tool_output["output"]
        emit(f"TOOL RESULT: {result}")

    if not tool_outputs:
        emit("No skill was requested in the selection cycle.")
    full_skill_chars = sum(call["chars"] for call in skill_calls if call["loaded"])
    emit(f"Full skill text supplied through tool results: {full_skill_chars} characters.")
    pause()

    emit("\n--- SKILLS CYCLE 2 OF 2: WRITE INCIDENT NOTE ---")
    emit(f"Writing call: previous_response_id={selection.id}; tools are not offered again.")
    final, writing_seconds = write_with_skills(
        client, model, selection, tool_outputs
    )
    final_text = final.output_text.strip()
    emit("FINAL INCIDENT NOTE:\n" + (final_text or "(empty response)"))
    pause()
    input_tokens, output_tokens, total_tokens = token_totals([selection, final])
    return {
        "mode": "skills",
        "status": "complete" if final_text else "empty_response",
        "output": final_text,
        "cycles": 2,
        "loaded_skills": list(
            dict.fromkeys(call["skill"] for call in skill_calls if call["loaded"])
        ),
        "skill_calls": skill_calls,
        "prompt_chars": len(selection_instructions) + len(brief),
        "skill_chars_in_prompt": 0,
        "full_skill_chars": full_skill_chars,
        "elapsed_seconds": round(selection_seconds + writing_seconds, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def run_agent(
    client: Any,
    model: str,
    brief: str,
    mode: str,
    catalog: dict,
    *,
    emit: Callable[[str], None] = print,
    pause: Callable[[], None] = lambda: None,
) -> dict:
    if mode == "basic":
        return run_basic(
            client, model, brief, catalog, emit=emit, pause=pause
        )
    if mode == "skills":
        return run_with_skills(
            client, model, brief, catalog, emit=emit, pause=pause
        )
    raise ValueError(f"Unknown mode: {mode}")
