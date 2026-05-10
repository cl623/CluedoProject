---
name: cluedo-project-report
description: >-
  Maintains and extends the Cluedo project report (Markdown draft exportable to
  PDF), updates sections as implementation progresses, and keeps placeholders for
  screenshots and testing evidence. Use when the user asks for project
  documentation, the assignment report, PDF, write-up, or to refresh docs after
  features ship.
---

# Cluedo project documentation agent

## Assignment requirements (verbatim)

Project Documentation (Up to 10-page PDF):
Create a comprehensive PDF document describing various aspects of your project:
Abstract: Briefly summarize the project’s purpose and goals.
Introduction: Explain the context and motivation behind developing the Cluedo game.
Game Rules: Clearly outline the rules and mechanics of the game.
Thorough Testing: Include screenshots demonstrating testing scenarios.
Challenges Faced: Discuss any obstacles encountered during development.
Stability and Reliability: Evaluate the game’s stability and reliability.
Additional Details: Cover any other relevant information.
Ensure the document is well-organized and visually appealing.

## Primary artifact

- Living draft: [docs/PROJECT_REPORT.md](../../PROJECT_REPORT.md) (version-controlled; export to PDF for submission).
- Optional figures folder: `docs/assets/` for screenshots (create when adding images).

## Responsibilities

1. **Keep the report current**  
   After meaningful code changes (new UI, rules, CLI flags), update the relevant sections in `docs/PROJECT_REPORT.md`: architecture, how to run, testing notes, challenges, stability.

2. **Structure**  
   Preserve the assignment section order. Use clear headings and short paragraphs; tables and bullet lists are encouraged for scannability.

3. **Testing section**  
   Maintain a numbered list of test scenarios. For each, include either:
   - a real screenshot path under `docs/assets/` and a one-line caption, or  
   - a bracketed placeholder, e.g. `[Screenshot: CLI new game — seed 42]` until the capture exists.

4. **Honesty**  
   Mark uncertain claims as draft (e.g. “planned” vs “implemented”). Do not invent test results.

5. **PDF export**  
   Remind that the Markdown source is the draft; PDF is produced externally (e.g. Pandoc, VS Code / Word print-to-PDF, or Typora). Do not require new dependencies in the repo for PDF generation unless the user asks.

6. **Style**  
   Write on behalf of the project (“we”), per author preference. Avoid naming specific assistant products.

## Workflow when the user asks to “update the report”

1. Read recent changes (git diff or key files named in the request).
2. Patch `docs/PROJECT_REPORT.md` only where facts changed.
3. If screenshots are missing, add TODO placeholders and a minimal list of recommended captures.
4. Keep total length reasonable for ≤10 pages when rendered (roughly 2500–4000 words depending on images).

## reference

- [docs/PROJECT_REPORT.md](../../PROJECT_REPORT.md) — canonical draft body.
