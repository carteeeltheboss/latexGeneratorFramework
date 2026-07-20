# Task: Generate a complete EMSI Beamer presentation

You are given an attached file named `presentation_template.tex`. Treat it as the authoritative visual and structural reference.

Create a complete, polished, compilable LaTeX Beamer presentation named `{{ main_file }}` from that template and the configuration below.

## Non-negotiable rules

1. Preserve the permanent EMSI identity, theme, typography, spacing, footer, title-page logic, figure tracking, and reusable TikZ visual language from the template.
2. EMSI branding is permanent. Organisation or partner branding is conditional and must appear only when `organisation.enabled` is true.
3. Do not create an empty organisation section. For a school project with no organisation, omit company history, company logo, department, company supervisor, and internship language entirely.
4. Adapt the narrative to `presentation.type`; do not force one fixed slide sequence on every presentation.
5. Use the requested duration and slide count as hard planning constraints. Prefer one clear idea per slide.
6. Use TikZ to explain systems, workflows, relationships, architecture, planning, and comparisons. Do not use TikZ as decoration and do not convert every slide into a diagram.
7. Interpret visual options as follows: `yes` = include, `no` = omit, `auto` = decide from the supplied facts.
8. Include PERT, Gantt, critical-path, or task-table slides only when requested or genuinely justified. Never invent task durations or dependencies. If required inputs are missing, create an explicit `[INFORMATION REQUIRED: ...]` placeholder.
9. Never fabricate results, KPIs, tests, citations, dates, organisation facts, technologies, screenshots, or repository details.
10. When information is missing, omit the optional slide or use a visible `[INFORMATION REQUIRED: ...]` placeholder rather than hallucinating.
11. Keep text concise. Convert dense explanations into diagrams, short bullets, callouts, timelines, tables, or staged flows.
12. Use only portable relative asset paths. Never use absolute Windows, macOS, or Linux paths.
13. Use uploaded assets only when they support a specific claim. Add useful captions and retain figure-list registration.
14. Keep the final source maintainable: meaningful comments, consistent TikZ styles, no dead code, no unused project-specific commands.
15. Escape LaTeX special characters correctly. Ensure every environment, brace, TikZ node, and path is closed.

## Presentation archetypes

Choose and adapt the most relevant narrative:

- `school_project`: academic context → problem → objectives/requirements → design → implementation → testing/demo → lessons/results → conclusion.
- `internship`: internship and organisation context → assigned mission → problem → methodology/planning → design → implementation → testing/results → professional learning → conclusion.
- `final_year_project`: context → problem → state of existing solution → requirements → methodology/planning → architecture/design → implementation → validation/results → limitations/roadmap → conclusion.
- `research_project`: research context → question/hypothesis → related work → methodology → experimental setup → results → interpretation → limitations → conclusion.
- `technical_demo`: use case → constraints → architecture → core workflow → implementation details → live/demo sequence → performance/testing → deployment/next steps.
- `custom`: infer the best structure from the supplied content while respecting all rules.

## Visual rules

- Reuse the template's `\slidepurpose`, `\tikzsolutionfigure`, `\solutionfigure`, PERT node, and TikZ style conventions.
- Prefer diagrams with short semantic labels over paragraphs.
- Architecture diagrams must show boundaries, components, flows, and ownership clearly.
- Workflow diagrams must show a meaningful sequence and inputs/outputs.
- Use-case and sequence diagrams must represent actual actors and interactions from the supplied facts.
- Gantt and PERT slides must remain readable at normal presentation scale.
- Screenshots should be framed, captioned, and used only when available.
- Avoid overly small text. Split overloaded slides.

## Branding rules

- Keep the EMSI logo path and placement from the template.
- If the fixed EMSI logo file is unavailable, keep the template's safe textual fallback.
- If `organisation.enabled` is true and a logo path exists, include the partner logo in the variable logo position.
- If `organisation.enabled` is false or the partner logo is missing, remove the partner-logo block cleanly.

## Output and compilation

- Requested target: `{{ output_target }}`.
- Requested compiler: `{{ compiler }}`.
- Main file: `{{ main_file }}`.
- Return a complete source file, not a patch and not a fragment.
- The source must compile independently after the listed assets are placed at their relative paths.
- Do not require shell escape unless `output.shell_escape` is true.
- For Overleaf, keep `main.tex` at the project root.
- For local builds, remain compatible with `latexmk` and the selected compiler.
- End your response with a short asset manifest listing required and optional files. Do not include long explanations outside the generated artifact.

## Project configuration

The following YAML is the source of truth. Do not reinterpret `no` as optional, and do not infer organisation details when `organisation.enabled` is false.

```yaml
{{ project_yaml }}
```

## Final self-check before returning

Verify all of the following:

- The slide structure matches the presentation type.
- No irrelevant company or internship slide exists.
- EMSI branding is preserved.
- The requested visual modules are honoured.
- The target duration and slide count are plausible.
- No fact was invented.
- All asset paths are relative.
- The LaTeX source is syntactically complete.
- The selected compiler is appropriate for the packages used.
- The result is presentation-ready rather than a lightly edited placeholder deck.
