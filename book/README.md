# Enzyme De Novo Design — Book Source

A Pearson-style graduate textbook built from the syllabus: 6 Parts, 27 chapters,
8 appendices, full pedagogical apparatus. Rendered to **PDF** (WeasyPrint) and
**DOCX** (pandoc) from one Markdown source set.

## Deliverables
- `dist/Enzyme_De_Novo_Design.pdf` — 405-page typeset book (showpiece layout)
- `dist/Enzyme_De_Novo_Design.docx` — editable Word version with matching styles

## Layout
- `content/` — one Markdown file per chapter (`chNN.md`), appendix (`appX.md`), and front-matter section (`fm_*.md`)
- `assets/figures/` — 24 technical figures (matplotlib, book palette)
- `style/book.css` — the PDF design system (paged media)
- `build/figures.py` — regenerate all figures
- `build/make_reference.py` — build the Word style template (`reference.docx`)
- `build/filters/boxes.lua` — maps callout divs to Word styles
- `build/build.py` — assemble + render both outputs
- `AUTHORING_GUIDE.md` — the chapter template / markup contract

## Rebuild
```bash
pip install weasyprint python-docx matplotlib numpy        # + pandoc, fonts
python3 build/figures.py            # (re)generate figures
python3 build/make_reference.py     # (re)build Word reference styles
python3 build/build.py              # render dist/*.pdf and dist/*.docx
```
Fonts: Source Serif 4 (body), Source Sans 3 (headings), IBM Plex Mono (code).
