"""The evaluator's structured, inferential review."""

from pydantic import BaseModel


# ========================
# Each criterion carries a score and rationale so students can see why the
# evaluator judged a candidate as it did.
# ========================
class CriterionScore(BaseModel):
    score: int
    rationale: str


# ========================
# This is the shape requested from the independent evaluator. The five scores
# are inferential judgments; feedback tells the generator what to reconsider.
# ========================
class Evaluation(BaseModel):
    evidence_grounding: CriterionScore
    causal_reasoning: CriterionScore
    completeness: CriterionScore
    uncertainty: CriterionScore
    actionability: CriterionScore
    overall_score: float
    biggest_weakness: str
    feedback: str
