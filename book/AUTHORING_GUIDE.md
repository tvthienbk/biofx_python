# Authoring Guide — Enzyme De Novo Design

Every chapter is a single Markdown file (`chNN.md`) rendered to **both** a
WeasyPrint PDF and a Word DOCX. Follow these conventions exactly so both
renderers behave. **Do not** write the "Chapter N" kicker (the build adds it).
Start each file with the `# Title`.

## Inline conventions
- Variables/quantities in Unicode, not LaTeX: `ΔG‡`, `k_cat`, `K_M`, `k_cat/K_M`,
  `10⁴ M⁻¹s⁻¹`, `pK_a`, `Å`, `°C`. Use `*italic*` for emphasis, `**bold**` for key terms at first use.
- **Never use `$…$` math.** Write equations as Unicode on their own centered line:
  `<p class="eqn">k = (k_B·T / h) · e^(−ΔG‡/RT)</p>` (raw HTML is allowed).
- Citations inline as `(Author, Year)`; full refs go in Further Reading.

## Figures (only reference figures that exist in assets/figures/)
```
![**Figure N.k** One-sentence caption explaining the takeaway.](assets/figures/NAME.png)
```

## Required chapter skeleton (in this order)
```
# Chapter Title

::: {.epigraph}
"Epigraph quote."
::: {.attrib}
— Attribution
:::
:::

::: {.outline data-title="Chapter Outline"}
**N.1** Section · **N.2** Section · **N.3** Section · …
:::

::: {.objectives data-title="Learning Objectives"}
After studying this chapter, you will be able to:

1. Objective text. [Understand]{.bloom .understand}
2. Objective text. [Apply]{.bloom .apply}
:::

::: {.synopsis data-title="Synopsis"}
2–4 sentences on what each section delivers.
:::

## N.1 First Section Title
Prose… (several substantial paragraphs). Introduce **key terms** in bold.

## N.2 …
… interleave the boxes below at natural points …

## Chapter Summary
- **N.1** One-line consolidation.
- **N.2** …

## Key Terms
term one, term two, term three, …

## Problem Set
**Review.** 1. … 2. … (write as a numbered list)

**Quantitative & Computational.** 1. … 2. …

**Challenge.** 1. …

## Further Reading
- Author, A. (Year). *Title*. Venue. — one-line annotation.
```

## Box types (all use `::: {.CLASS data-title="…"} … :::`)
- `.conceptcheck` — "Concept Check N.1" — 1–2 short formative questions.
- `.worked` — "Worked Example N.k · Title" — start **Problem.** then **Solution.** with steps.
- `.method` — "Method N.k · Title" — numbered protocol steps.
- `.toolbox` — "Tool Box N.k · Title" — version-stamped software list.
- `.reality` — "Reality Check N.k" — honest success rates / limits.
- `.redflags` — "Red Flags N.k" — reviewer-catching mistakes (use a list).
- `.bench` — "From the Bench N.k" — wet-lab perspective.
- `.ethics` — "Ethics & Responsibility N.k" — where specified.
- `.lab` — "Hands-On Lab N · Title" (methods chapters) — end with a line
  `**Platform:** … · **Deliverable:** …`
- `.studio` — "Studio Exercise N · Title" (conceptual chapters) — same ending line.

## Bloom tags
`[Understand]{.bloom .understand}` `[Apply]{.bloom .apply}` `[Analyze]{.bloom .analyze}`
`[Evaluate]{.bloom .evaluate}` `[Create]{.bloom .create}`

## Quality bar
Write genuine, accurate graduate-level content — real mechanisms, real numbers,
correct tool names/versions, honest hit rates. No placeholder text. Target the
page count implied by the syllabus (substantial: ~1,800–3,500 words of body prose
per chapter plus the boxes).
