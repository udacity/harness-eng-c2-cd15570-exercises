# On-Demand Marketing Skills: Student Exercise

## The use case

A marketing manager is launching **InspectAI**, an industrial inspection product that analyzes equipment photographs for visible signs of wear and damage. The manager needs copy for LinkedIn, email, a landing page, a newspaper ad, and a trade-magazine ad. The six files in [campaigns](campaigns) provide the requests. The six complete [skills](skills) files contain channel and brand guidance.

The harness compares two ways of supplying that guidance to the same model and brief:

| Mode | What happens |
| --- | --- |
| `basic` | The supplied one-call path sends all six complete `SKILL.md` files with every request, even when the request asks for one channel. |
| `skills` | Your two-cycle path first shows only skill names and short descriptions. The model requests relevant full files through `load_skill`, then writes the campaign using those files. |

The goal is to make the skill-selection step visible and evaluate the tradeoff. A shorter skill payload may reduce tokens while the extra model call increases latency. Check the copy as well as the numbers; a model can miss a requested asset or make an unsupported claim in either mode.

## What is supplied and what you build

The starter includes the six campaign briefs and six complete skill files, model and CLI setup, run logging, Return-to-continue pauses, token and time reporting, and a working `basic` mode. The `skills` mode has TODOs and raises `NotImplementedError` until you complete it. Keep the supplied briefs and skills intact for the first comparison so both modes receive the same task and guidance.

Complete these parts:

1. **[catalog.py](catalog.py):** Implement `catalog_prompt` so the selection cycle receives each skill's name and frontmatter description, with no full skill body. `discover_skills` and `load_skill` are supplied. The latter validates names against the catalog before reading a file.
2. **[agent.py](agent.py):** Define the `load_skill` function-tool schema with one required string argument, `skill_name`. The schema should reject additional properties.
3. **[agent.py](agent.py):** Implement `build_selection_instructions` so cycle 1 contains the base rules and short catalog. Implement `resolve_skill_call` so valid requests become full-text `function_call_output` items and malformed or unknown requests become error results without reading another file.
4. **[agent.py](agent.py):** Implement `write_with_skills` to continue from the selection response ID without offering tools. Then implement `run_with_skills` to connect both cycles, print and pause after each, and return the result fields used by the comparison table. The no-skill case must still produce a final campaign.
5. **[skills/magazine_ad/SKILL.md](skills/magazine_ad/SKILL.md):** After your first paired comparison, make one targeted improvement to the magazine guidance based on an issue you observe in the ad. Keep its routing description short and put the detailed change in the body. Rerun the magazine brief in `skills` mode and describe what changed in the copy. The model may not follow the revised guidance perfectly; use the output as evidence rather than assuming success.

The function docstrings name the expected inputs and result fields. Use the completed `run_basic` as a reference for printing, timing, token totals, and the result dictionary. `main.py` and `run_log.py` are supplied harness code.

## Set up

Use Python 3.12 or a compatible Python 3 installation. From `module-2-skills/exercise-skills-starter/`:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Put your Vocareum API key in `.env`:

```dotenv
OPENAI_API_KEY=your-vocareum-api-key
OPENAI_MODEL=gpt-4.1-mini
```

`OPENAI_MODEL` is optional and defaults to `gpt-4.1-mini`. The code uses the OpenAI Python client with `https://openai.vocareum.com/v1`. `.env` and generated logs are ignored by Git.

## Run and inspect

Start with the supplied mode:

```bash
python3 main.py basic --campaign inspectai_email
```

After completing the TODOs, compare a single-channel request, a print ad, and the combined campaign:

```bash
python3 main.py compare --campaign inspectai_email
python3 main.py compare --campaign inspectai_magazine
python3 main.py compare --campaign inspectai_campaign
```

`python3 main.py compare --campaign all` runs all six briefs. Each `basic` run has one model cycle; each `skills` run has a selection cycle and a writing cycle. Press **Return** after every cycle. The first line of the run gives the path to a timestamped `output/` log containing the brief, tool calls, campaign copy, and comparison table.

For each brief, check which skills the model requested. A single-channel brief should normally load its matching channel skill; the combined brief calls for LinkedIn, email, website, and brand voice. The table reports full skill characters supplied, API input and output tokens, total tokens, and model seconds. Its `change` row compares `skills` with `basic`: negative percentages mean less, positive percentages mean more. Full skill characters count source text, not API tokens or the entire context.

Write a short run note explaining which skills were relevant, whether every requested asset appeared, whether the claims stayed within the brief, and how tokens and time changed. Include the magazine skill revision and its observed effect. Live model choices vary, so there is no required winner, fixed percentage, or guaranteed wording change.

## Completion check

- [ ] `basic` still runs with all six full skill files in its prompt.
- [ ] The `skills` selection prompt contains names and descriptions, with full skill bodies returned only for requested names.
- [ ] Valid `load_skill` calls produce tool results; unknown names produce an error result without reading another path.
- [ ] The second cycle writes a final campaign, including when no skill was selected, and pauses after both cycles.
- [ ] The comparison table shows loaded skills, full skill characters, tokens, time, and percentage changes for paired runs.
- [ ] A targeted edit to the magazine skill can be loaded without changing the catalog reader, agent routing code, or CLI.
- [ ] Your run note uses the saved log to discuss context relevance, copy quality, and the token–latency tradeoff.

## Repository map

```text
exercise-skills-starter/
├── campaigns/               # six supplied InspectAI requests
├── skills/                  # six supplied SKILL.md files
├── catalog.py               # catalog_prompt TODO
├── agent.py                 # tool, selection, loading, writing TODOs; working basic mode
├── main.py                  # supplied CLI and comparison table
├── run_log.py               # supplied terminal-to-file logging
├── .env.example
├── requirements.txt
└── README.md
```
