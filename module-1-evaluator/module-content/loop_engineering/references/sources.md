# Sources and Research Notes

Accessed October 14, 2026. Prefer the linked paper or official publication
page when adapting claims for slides.

## R1 — Self-Refine

**Aman Madaan et al.** “Self-Refine: Iterative Refinement with Self-Feedback.”
NeurIPS 2023.  
[Conference paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/91edff07232fb1b55a505a9e9f6c0ff3-Paper-Conference.pdf) ·
[arXiv](https://arxiv.org/abs/2303.17651)

**Relevant use:** Evidence that iterative self-feedback can improve output on a
range of tasks. This source is why the module must not claim that self-review
always fails.

**Guardrail:** The paper's positive results do not establish that self-review
is sufficient as a production acceptance boundary for arbitrary tasks.

## R2 — Limits of intrinsic self-correction

**Jie Huang et al.** “Large Language Models Cannot Self-Correct Reasoning Yet.”
ICLR 2024.  
[OpenReview](https://openreview.net/forum?id=IkmD3fKBPQ) ·
[arXiv](https://arxiv.org/abs/2310.01798)

**Relevant use:** The paper studies reasoning self-correction without external
feedback and reports that correction can fail or degrade performance in the
examined settings.

**Guardrail:** Do not generalize the title into “all LLM self-evaluation always
fails.” The module describes a risk and a boundary-design response.

## R3 — LLM-as-a-judge and bias

**Lianmin Zheng et al.** “Judging LLM-as-a-Judge with MT-Bench and Chatbot
Arena.” NeurIPS 2023 Datasets and Benchmarks.  
[Conference paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf) ·
[arXiv](https://arxiv.org/abs/2306.05685)

**Relevant use:** Supports discussion of model-based judging and documented
limitations such as position, verbosity, and self-enhancement bias.

**Guardrail:** Do not imply those are the only biases or that one mitigation
proves an evaluator unbiased. Calibrate on the intended task distribution.

## R4 — Reflexion

**Noah Shinn et al.** “Reflexion: Language Agents with Verbal Reinforcement
Learning.” NeurIPS 2023.  
[Conference paper](https://papers.nips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html) ·
[arXiv](https://arxiv.org/abs/2303.11366)

**Relevant use:** Demonstrates that language feedback can be incorporated into
future attempts and that feedback sources may be internal or external.

**Guardrail:** Reflexion is a specific agent method. The course controller is
not claimed to implement that complete method.

## R5 — Model-written critiques

**Nat McAleese et al.** “LLM Critics Help Catch LLM Bugs.” 2024.  
[arXiv](https://arxiv.org/abs/2407.00215) ·
[Research paper](https://cdn.openai.com/llm-critics-help-catch-llm-bugs-paper.pdf)

**Relevant use:** Supports the claim that a critic model can help identify
errors in model-written code and can assist human evaluation.

**Guardrail:** The work focuses on particular critique tasks and models. The
critics are not perfectly correct, and results should not be transferred to
incident communication without validation.

## R6 — AI-assisted critique for human review

**OpenAI.** “Self-critiquing models for assisting human evaluators.” 2022.  
[Paper](https://cdn.openai.com/papers/critiques.pdf) ·
[Project page](https://openai.com/index/critiques/)

**Relevant use:** Illustrates a human-in-the-loop use of model-written critiques
and the value of showing flaws rather than returning only a scalar score.

**Guardrail:** AI assistance improves some studied review settings; it does not
replace human judgment or deterministic verification universally.

## R7 — Generative adversarial networks

**Ian Goodfellow et al.** “Generative Adversarial Networks.” 2014.  
[arXiv](https://arxiv.org/abs/1406.2661)

**Relevant use:** Provides the origin for the limited producer-versus-
discriminator analogy in Video 2.

**Guardrail:** A generator–evaluator harness at inference time is not a GAN. It
does not jointly train two networks through a minimax objective.

## R8 — Constitutional AI

**Yuntao Bai et al.** “Constitutional AI: Harmlessness from AI Feedback.” 2022.  
[arXiv](https://arxiv.org/abs/2212.08073)

**Relevant use:** An example of making evaluation principles explicit and using
AI-generated feedback within a larger training and supervision procedure.

**Guardrail:** The course module concerns inference-time harness evaluation,
not Constitutional AI training.

## R9 — IKEA effect analogy

**Michael I. Norton, Daniel Mochon, and Dan Ariely.** “The IKEA Effect: When
Labor Leads to Love.” *Journal of Consumer Psychology* 22, no. 3 (2012).  
[DOI](https://doi.org/10.1016/j.jcps.2011.08.002)

**Relevant use:** Source for the human-behavior analogy about overvaluing work
one helped create.

**Guardrail:** This is not evidence that language models experience ownership,
effort justification, or a universal equivalent of the human effect. Keep it
as an analogy and ground the engineering argument in observed evaluator errors.

## Claim-to-source map

| Course claim | Sources | Approved phrasing |
| --- | --- | --- |
| Self-feedback can improve candidates | R1, R4 | “Self-feedback can help on some tasks.” |
| Intrinsic self-correction has demonstrated limits | R2 | “Without external feedback, studied reasoning tasks sometimes fail to improve or degrade.” |
| LLM judges can exhibit systematic bias | R3 | “Position, verbosity, and self-enhancement biases have been documented.” |
| Critics can help expose model errors | R5, R6 | “Model-written critiques can improve error detection in studied settings.” |
| Generator/evaluator resembles adversarial roles | R7 | “The producer/critic split is an analogy, not GAN training.” |
| Explicit principles can guide AI feedback | R8 | “Explicit criteria make AI feedback more inspectable.” |
| Authors may overvalue created work | R9 | “The IKEA effect is a human analogy only.” |

## Citation and slide policy

1. Put short citations in speaker notes rather than crowding slides.
2. Attribute empirical numbers only to the exact study and task setting.
3. Do not combine results from different papers into a synthetic benchmark.
4. Mark course-created metrics as illustrative unless generated by a documented
   run.
5. Recheck links and publication status before final recording.
