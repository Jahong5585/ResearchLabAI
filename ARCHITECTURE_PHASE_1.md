# Architecture Phase 1 — Analytical Synthesis Layer

## Problem confirmed in the original code

The original Writer received article-level facts and was explicitly forbidden to combine or interpret them. Therefore it could produce a safe summary, but it could not generate a genuine analytical literature review.

## Architecture selected

The existing pipeline was preserved. Only one new responsibility was introduced:

```text
Summarizer → Cluster → Outline → Synthesis → Writer
```

A single Synthesis Agent was selected instead of separate Comparison, Trend, Gap, Methodology, and Contradiction agents. This avoids unnecessary orchestration complexity while keeping the responsibility clear: all cross-paper analysis occurs before Writer.

## Data contract

```text
ArticleSummary[]
  ↓
SynthesisContextBuilder
  ↓
SynthesisAgent
  ↓
SynthesisReport
  ├── SynthesisClaim[]
  ├── aggregate statistics
  ├── methodology patterns
  ├── trends
  ├── contradictions
  ├── recurring limitations
  └── gaps
```

## Safety rules

- Every claim must reference supporting article numbers.
- Invalid article numbers are detected.
- Claims without supporting articles are removed.
- The same article cannot simultaneously support and contradict one claim.
- Writer cannot operate as an analyst when the synthesis report is absent.
- API errors are raised instead of being parsed as scientific content.

## Files added

- `Agents/Synthesis/synthesis_agent.py`
- `Core/article_summary_parser.py`
- `Core/synthesis_context_builder.py`
- `Core/synthesis_engine.py`
- `Models/synthesis_claim.py`
- `Models/synthesis_report.py`
- `Prompts/synthesis.txt`

## Files changed

- `Agents/Planner/planner.py`
- `Agents/Reviewer/reviewer.py`
- `Agents/Summarizer/summarizer.py`
- `Agents/Writer/writer.py`
- `Config/settings.py`
- `Core/agent_registry.py`
- `Core/query_optimizer.py`
- `Core/task.py`
- `Core/workflow_builder.py`
- `Models/article_summary.py`
- `Prompts/reviewer.txt`
- `Prompts/summarizer.txt`
- `Prompts/writer.txt`
- `Providers/manager.py`
- `Providers/gemini_provider.py`
- `Providers/openrouter_provider.py`

## Not changed intentionally

- Search architecture was not expanded to additional databases.
- Cluster was not replaced with embeddings.
- Full PDF processing was not added.
- Reviewer revision loop was not added.
- Existing EvidenceBuilder was retained for compatibility.

These changes belong to later stages and are not required to validate the new synthesis boundary.
