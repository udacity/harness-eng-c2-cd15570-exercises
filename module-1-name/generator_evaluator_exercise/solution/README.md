# Reference solution

Run `python -m solution.main` from the project root after following the
[setup instructions](../README.md). The loop in `main.py` makes the control
flow visible: generate a candidate, get a separate structured review, stop
at 4.2/5 or three attempts, or pass feedback into a new generator request.

`generator.py` always supplies the incident and original task. A revision
also includes the prior answer and evaluator feedback. `evaluator.py` creates
a fresh input list with its own system prompt and sees only the incident,
task, and current candidate. The evaluator can use the same underlying model;
its invocation and context remain separate.

`self_evaluation_demo.py` optionally asks the generator to score its own
answer in the same conversation, then independently reviews that original
answer. The two scores are observations for comparison, not a guarantee that
self-evaluation is wrong every time.
