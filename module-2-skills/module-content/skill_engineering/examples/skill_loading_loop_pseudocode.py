"""Provider-shaped pseudocode for a bounded, on-demand skill-loading loop."""

import json
from typing import Any


MAX_SKILLS_PER_TASK = 4

LOAD_SKILL_TOOL = {
    "type": "function",
    "name": "load_skill",
    "description": "Load one relevant skill from the trusted catalog.",
    "parameters": {
        "type": "object",
        "properties": {"skill_name": {"type": "string"}},
        "required": ["skill_name"],
        "additionalProperties": False,
    },
    "strict": True,
}


def run_with_skills(client: Any, model: str, task: str, catalog: dict) -> dict:
    """Select once, resolve safely, then write without the loading tool."""

    selection = client.responses.create(
        model=model,
        instructions=(
            "Request every relevant skill, then stop. Do not answer the task.\n"
            + render_metadata_only(catalog)
        ),
        input=task,
        tools=[LOAD_SKILL_TOOL],
    )

    outputs: list[dict] = []
    loaded: list[dict] = []
    seen: set[str] = set()

    for item in selection.output:
        if item.type != "function_call":
            continue
        if len(outputs) >= MAX_SKILLS_PER_TASK:
            outputs.append(error_output(item.call_id, "skill limit exceeded"))
            continue

        try:
            if item.name != "load_skill":
                raise ValueError("unsupported tool")
            arguments = json.loads(item.arguments)
            if not isinstance(arguments, dict) or set(arguments) != {"skill_name"}:
                raise ValueError("expected only skill_name")
            name = arguments["skill_name"]
            if not isinstance(name, str):
                raise ValueError("skill_name must be a string")
            if name in seen:
                raise ValueError("duplicate skill request")

            # The loader looks up an exact catalog key. It never opens `name`.
            text, provenance = load_exact_allowlisted_skill(name, catalog)
            seen.add(name)
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": text,
                }
            )
            loaded.append({"name": name, "source": provenance, "chars": len(text)})
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            outputs.append(error_output(item.call_id, str(error)))

    writing_input: Any = outputs or "No skill was selected. Complete the task."
    final = client.responses.create(
        model=model,
        instructions=(
            "Complete the task using valid loaded guidance. Base policy and "
            "runtime controls take precedence over skill text."
        ),
        previous_response_id=selection.id,
        input=writing_input,
        # Deliberately omit tools: selection is closed for this simple design.
    )

    return {
        "output": final.output_text,
        "loaded_skills": loaded,
        "cycles": 2,
    }


def render_metadata_only(catalog: dict) -> str:
    return "\n".join(
        f"- {name}: {entry['description']}" for name, entry in catalog.items()
    )


def load_exact_allowlisted_skill(name: str, catalog: dict) -> tuple[str, str]:
    if name not in catalog:
        raise ValueError(f"unknown skill: {name}")
    entry = catalog[name]
    return entry["text"], entry["source"]


def error_output(call_id: str, message: str) -> dict:
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": f"ERROR: {message}",
    }
