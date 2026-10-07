https://github.com/vivek-bhushan/vivek-bhushan-IITM-WEEK27
# Week 27 Graded Mini Project

## Policy Assistant Agent — Vivek Bhushan

I built a grounded Policy Assistant over the supplied ten-record policy corpus. The system uses local FAISS retrieval, typed tools, deterministic ReAct-style tracing, bad-ID recovery, critic-verified memory, explicit graph budgets, one retry, structured evaluation, and automated tests.

## Recorded results

- All 9 canned policy questions passed with the expected document IDs.
- Bad-ID recovery successfully moved from a typed read error to policy search.
- The repeated password question produced a verified warm-memory hint.
- A two-node graph budget stopped explicitly with `budget_exhausted`.
- All 6 PyTests passed.

## Submission contents

The ZIP contains the executed Colab notebook, supplied dataset, modular Python code, requirements, evaluation runner, logs, tests, README, Markdown companion, and the final PDF report with Colab screenshots.

## Project summary

The main learning for me was that the final wording is only one part of a dependable agent. Search, full-source reading, exact citations, quotation verification, memory write conditions, retry limits, and stop rules each prevent a different failure mode. The completed system is intentionally lightweight, but its behaviour is visible, reproducible, and easy to test.
