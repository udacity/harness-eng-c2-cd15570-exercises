# Student starter

Your goal is to make the incident-analysis generator, independent evaluator,
and harness loop work together. Read the shared incident in `shared/case.py`
and the review shape in `shared/models.py`. Setup is in the [project README](../README.md).

Complete the four `TODO` markers:

1. In `generator.py`, invoke the generator with its system prompt and the
   incident/task. Return its full text and reported usage. On later attempts,
   include the previous response and feedback in the generator's user message.
2. In `evaluator.py`, make a separate `responses.parse` call with the
   independent reviewer prompt and `text_format=Evaluation`. Its input should
   contain the incident, original task, and current candidate only.
3. In `main.py`, run generator → evaluator → score check for at most three
   attempts. Print each attempt and the final score change. The harness owns
   the 4.2 stopping threshold and tracks token usage when reported.
4. In `main.py`, if a revision is allowed, pass `evaluation.feedback` and the
   current candidate to the next generator call. Ask for another complete
   analysis, rather than an addendum.

Before you fill in the loop, `python -m starter.main` prints the TODO 3
instruction without making an API request. After that, the generator and
evaluator skeletons will point you to their remaining TODOs. Compare your
completed implementation with `solution/` after trying the exercise.
