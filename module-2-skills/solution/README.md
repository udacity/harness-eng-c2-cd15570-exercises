# Marketing Campaign Skills Harness

## Use case

A marketing manager is launching **InspectAI**, a product that analyzes equipment photographs for signs of wear and damage. The manager needs campaign copy for LinkedIn, email, a website, newspaper ads, and trade-magazine ads. Each channel has writing guidance in a `SKILL.md` file, and a brand-voice skill helps keep a combined campaign consistent.

## Exercise objective

Run the **same campaign requests** through `basic` and `skills` to see what progressive disclosure changes. The central question is whether the model receives guidance relevant to the current request. Token use and latency measure the cost of that choice; they are not the only measures of success.

1. Run `python3 main.py compare --campaign all`. For each single-channel brief, compare the six full skills in `basic` with the names requested through `load_skill` in `skills`. Record any irrelevant skill text sent by `basic` and any relevant skill the model failed to load.
2. Inspect the combined campaign. Check whether the model composes the channel skills with `brand_voice`, and whether the output includes all three assets with consistent claims and the requested calls to action.
3. Record **full skill characters supplied**, **total API tokens**, and **model seconds**, including the percentage change from `basic` to `skills` in the comparison table. Explain the tradeoff shown by each measure. Review the copy for unsupported claims; a smaller context does not guarantee better writing.
4. Find the email guidance in `skills/email_marketing/SKILL.md`. Explain how you would change an email rule without editing `agent.py` or `catalog.py`. For a hands-on check, temporarily add a specific, safe writing rule to that skill, rerun the email in `skills` mode, and then restore the rule.

There is no expected winner for every request. The run directly demonstrates selective loading and composition. The independent skill files make a maintenance change possible without changing the harness; scaling that pattern to a larger catalog is a design implication, not a benchmark established by six skills.

| Benefit to look for | Evidence in this exercise |
| --- | --- |
| Relevant context | A single-channel request can load its matching skill while `basic` supplies all six full files. |
| Composition | The combined request can load channel guidance alongside `brand_voice`. |
| Maintainability | An email rule lives in `email_marketing/SKILL.md`; the loading code does not need a channel-specific branch. |
| Measured tradeoff | Full skill characters, API tokens, model time, and copy quality can move in different directions. |

This solution compares two ways to give that guidance to the same model and campaign brief:

| Mode | What the model receives | Model cycles |
| --- | --- | --- |
| `basic` | The brief, a basic instruction, and the **full text of all six skills** in the prompt, even if the brief requests only one channel. | One call writes the campaign. |
| `skills` | The brief, a basic instruction, and **skill names with short descriptions**. The model requests relevant skills through `load_skill`; the harness reads those files and returns their contents. | Cycle 1 selects and loads skills. Cycle 2 writes the campaign using the loaded guidance. |

The model decides which skills to request in cycle 1; the Python harness validates the names, reads the files, and returns their text as tool results. In cycle 2, the tool is no longer offered so the model writes the response. If it selects no skill, the run still completes and reports that no skill was loaded. A combined brief can request several skills in the first cycle.

For a single-channel request, `basic` supplies every complete skill while `skills` starts with short routing descriptions and returns selected full files as tool results. The combined request calls for the original three channels plus brand voice, so it can use four of the six available skills. The extra model call can still make `skills` slower, even when it uses fewer total tokens. Inspect the copy too; neither architecture guarantees that the model follows every instruction.

## Campaigns and skills

The [campaigns](campaigns) folder contains six detailed InspectAI requests. Five ask for one asset: [LinkedIn](campaigns/inspectai_linkedin.txt), [email](campaigns/inspectai_email.txt), [website copy](campaigns/inspectai_website.txt), a [newspaper ad](campaigns/inspectai_newspaper.txt), or a [trade-magazine ad](campaigns/inspectai_magazine.txt). The [combined campaign](campaigns/inspectai_campaign.txt) asks for the original three assets and a consistent voice. Each brief includes audience, workflow, placement, and claim boundaries that help the model choose relevant guidance. Both modes receive the **same brief** in separate, fresh conversations; extra brief detail also adds tokens to both modes.

The [skills](skills) folder contains [brand voice](skills/brand_voice/SKILL.md), [LinkedIn marketing](skills/linkedin_marketing/SKILL.md), [email marketing](skills/email_marketing/SKILL.md), [website copy](skills/website_copy/SKILL.md), [newspaper ads](skills/newspaper_ad/SKILL.md), and [trade-magazine ads](skills/magazine_ad/SKILL.md). Each file has a short routing description in its frontmatter and detailed instructions below it. `catalog.py` reads the descriptions for the skills prompt; `load_skill` reads a full file only when requested. Basic mode reads all six full files when building its prompt. The detailed skill bodies make this context difference especially visible for single-channel briefs, while the combined brief does not require the two print-ad skills.

## Set up

From `module-2-skills/solution/`:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Put your Vocareum API key in `.env`:

```dotenv
OPENAI_API_KEY=your-vocareum-api-key
OPENAI_MODEL=gpt-4.1-mini
```

`OPENAI_MODEL` is optional and defaults to `gpt-4.1-mini`. The code uses the OpenAI Python client with `https://openai.vocareum.com/v1`. `.env` and run logs are ignored by Git.

## Run and compare

The default command runs the combined campaign through both modes:

```bash
python3 main.py
```

Run a single campaign or every supplied campaign:

```bash
python3 main.py compare --campaign inspectai_linkedin
python3 main.py compare --campaign inspectai_newspaper
python3 main.py compare --campaign inspectai_magazine
python3 main.py compare --campaign all
python3 main.py basic --campaign inspectai_email
python3 main.py skills --campaign inspectai_website
```

You can also submit your own UTF-8 brief with `python3 main.py compare --brief-file /path/to/brief.txt`.

The terminal prints each cycle, the selected skill names and source paths, the final campaign, and a comparison table. It pauses **after every cycle**, including final cycles. Press **Return** to continue. A timestamped file under `output/` saves everything printed to the screen; the first line shows its path.

The table shows how many characters of complete `SKILL.md` text each mode supplied, input, output, and total tokens reported by the API, and the sum of model-call durations. A `change` row follows each paired result and shows `(skills - basic) / basic` as a percentage; negative values mean the skills run used less or took less time. A percentage is `n/a` when the basic value is zero or either value is missing. Full skill characters are a source-text measure, not an API token count or a measure of the entire model context. `basic` sends them in its prompt; `skills` returns selected files through `load_skill`. Time spent waiting for Return is excluded. If the endpoint omits usage data, token columns show `None`. The two modes use the same configured model; their conversations do not share previous responses or loaded skills.

## Code map

| File | Role |
| --- | --- |
| [main.py](main.py) | Selects campaigns and modes, prints the comparison, and saves the run log. |
| [agent.py](agent.py) | Contains the one-call basic path and two-cycle skill path. |
| [catalog.py](catalog.py) | Discovers skill descriptions and loads requested `SKILL.md` files. |
| [run_log.py](run_log.py) | Copies terminal output to the run log. |
