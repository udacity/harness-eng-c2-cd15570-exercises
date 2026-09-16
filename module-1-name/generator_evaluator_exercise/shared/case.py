"""A fictional incident with competing explanations, not a single exact answer."""

# ========================
# The incident includes clues and competing explanations. Its ambiguity makes
# reasoning and uncertainty more useful than choosing one exact answer.
# ========================
INCIDENT = """Incident: API Latency After Release

A customer-facing API normally responds in about 200 ms. Shortly after a new
release, median latency rose to about 4 seconds. CPU utilization stayed near
normal. Memory utilization increased slightly but remained within limits.
Database connections increased significantly, and application logs show
intermittent database timeout errors. Incoming customer request volume remained
approximately unchanged.

The release introduced automatic retries for failed database requests.
Restarting application workers temporarily restored normal latency, but after
about 30 minutes latency began rising again.

Engineers proposed five explanations: the database server lacks CPU; the
application has a memory leak; the database connection pool is exhausted; the
new retry mechanism amplifies database load; or network latency between the
application and database has increased. No measurements of database CPU,
connection-pool wait time, retry rate, or network latency are available yet."""

# ========================
# Both components receive this original task. A generator revision also gets
# feedback, while an evaluator review stays anchored to this task and case.
# ========================
TASK = """Analyze the incident and determine the most likely explanation.
Explain your reasoning using the evidence provided. Discuss important
alternative explanations and uncertainties. Recommend the next actions the
engineering team should take to confirm the diagnosis and address the problem.
Produce approximately 400–700 words; no rigid answer format is required."""
