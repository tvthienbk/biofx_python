"""Build a weekly lecture deck (.pptx) from a list of slide dicts.

A small set of reusable slide layouts keeps every deck in the course visually
consistent: title, agenda, section divider, bulleted content (with an optional
highlight panel), two-column comparison, table, big-statement, and a numbered
workflow/steps slide.
"""
from __future__ import annotations

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

from . import theme

# 16:9 canvas (matches the original Week 1 deck)
EMU = 914400
SW = Inches(13.333)
SH = Inches(7.5)


def _rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)


def _bg(slide, color: str):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = _rgb(color)


def _box(slide, left, top, width, height, fill=None, line=None, line_w=1.0,
         shape=MSO_SHAPE.RECTANGLE, shadow=False):
    sp = slide.shapes.add_shape(shape, left, top, width, height)
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = _rgb(fill)
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = _rgb(line)
        sp.line.width = Pt(line_w)
    sp.shadow.inherit = False
    if shadow:
        el = sp._element.spPr
        effect = el.makeelement(qn('a:effectLst'), {})
        el.append(effect)
    return sp


def _text(slide, left, top, width, height, runs, align=PP_ALIGN.LEFT,
          anchor=MSO_ANCHOR.TOP, wrap=True, space_after=4, line_spacing=1.0):
    """runs: list of paragraphs; each paragraph is a list of (text, opts)."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    first = True
    for para in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.space_after = Pt(space_after)
        p.space_before = Pt(0)
        p.line_spacing = line_spacing
        if isinstance(para, str):
            para = [(para, {})]
        for txt, opt in para:
            r = p.add_run()
            r.text = txt
            r.font.size = Pt(opt.get("size", 18))
            r.font.bold = opt.get("bold", False)
            r.font.italic = opt.get("italic", False)
            r.font.name = opt.get("font", theme.FONT_BODY)
            r.font.color.rgb = _rgb(opt.get("color", theme.INK))
        if "bullet" in (para[0][1] if para and isinstance(para[0], tuple) else {}):
            pass
    return tb


def _footer(slide, week_no, page):
    _box(slide, 0, SH - Inches(0.42), SW, Inches(0.42), fill=theme.NAVY)
    _text(slide, Inches(0.5), SH - Inches(0.40), Inches(9), Inches(0.36),
          [[(f"{theme.COURSE_TITLE}   ·   Week {week_no}",
             {"size": 9, "color": "FFFFFF"})]], anchor=MSO_ANCHOR.MIDDLE)
    _text(slide, SW - Inches(1.2), SH - Inches(0.40), Inches(0.7), Inches(0.36),
          [[(str(page), {"size": 9, "color": "FFFFFF", "bold": True})]],
          align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def _kicker(slide, text):
    _text(slide, Inches(0.6), Inches(0.45), Inches(11), Inches(0.4),
          [[(text.upper(), {"size": 13, "bold": True, "color": theme.AMBER})]])


def _title(slide, text, color=theme.NAVY, size=30):
    _text(slide, Inches(0.6), Inches(0.85), Inches(12.1), Inches(1.0),
          [[(text, {"size": size, "bold": True, "color": color,
                    "font": theme.FONT_HEAD})]])
    _box(slide, Inches(0.62), Inches(1.7), Inches(1.4), Pt(3), fill=theme.AMBER)


# ---------------------------------------------------------------------------
# slide layouts
# ---------------------------------------------------------------------------

def slide_title(prs, s):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, theme.NAVY)
    _box(sl, 0, 0, SW, Inches(0.18), fill=theme.AMBER)
    _box(sl, 0, SH - Inches(0.18), SW, Inches(0.18), fill=theme.TEAL)
    # faint X -> Y motif
    _text(sl, Inches(0.7), Inches(0.6), Inches(6), Inches(0.5),
          [[(theme.COURSE_TITLE.upper(), {"size": 15, "bold": True,
                                          "color": theme.AMBER})]])
    _text(sl, Inches(0.7), Inches(2.5), Inches(12), Inches(2.2),
          [[(s["block"], {"size": 20, "color": theme.BLUE_LIGHT, "bold": True})],
           [(s["title"], {"size": 46, "bold": True, "color": "FFFFFF",
                          "font": theme.FONT_HEAD})]], space_after=10)
    _text(sl, Inches(0.7), Inches(4.7), Inches(11.5), Inches(1.2),
          [[(s["subtitle"], {"size": 18, "italic": True, "color": "D7DEEA"})]])
    _text(sl, Inches(0.7), Inches(6.2), Inches(11.5), Inches(0.6),
          [[(f"Week {s['number']}   ·   4-credit graduate seminar   ·   "
             "theory + assumptions + code + a real case",
             {"size": 13, "color": theme.GREY})]])
    return sl


def slide_section(prs, s, week_no):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, theme.NAVY)
    _box(sl, Inches(0.7), Inches(2.6), Inches(0.18), Inches(2.0), fill=theme.AMBER)
    _text(sl, Inches(1.1), Inches(2.4), Inches(11), Inches(0.6),
          [[(s.get("kicker", "PART").upper(), {"size": 15, "bold": True,
                                               "color": theme.AMBER})]])
    _text(sl, Inches(1.1), Inches(2.95), Inches(11.4), Inches(1.4),
          [[(s["title"], {"size": 40, "bold": True, "color": "FFFFFF",
                          "font": theme.FONT_HEAD})]])
    if s.get("subtitle"):
        _text(sl, Inches(1.1), Inches(4.4), Inches(10.8), Inches(1.4),
              [[(s["subtitle"], {"size": 18, "italic": True, "color": "C7D2E2"})]])
    return sl


def _bullets_runs(bullets):
    runs = []
    for b in bullets:
        if isinstance(b, tuple):  # (text, level)
            text, level = b
        else:
            text, level = b, 0
        marker = "—  " if level == 0 else "·  "
        col = theme.INK if level == 0 else theme.NAVY_SOFT
        size = 18 if level == 0 else 15
        runs.append([(marker, {"color": theme.AMBER if level == 0 else theme.GREY,
                               "bold": True, "size": size}),
                     (text, {"size": size, "color": col})])
    return runs


def slide_content(prs, s, week_no, page):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, theme.PAPER)
    _kicker(sl, s.get("kicker", ""))
    _title(sl, s["title"])
    has_panel = bool(s.get("note"))
    body_w = Inches(7.7) if has_panel else Inches(12.1)
    _text(sl, Inches(0.6), Inches(2.05), body_w, Inches(4.6),
          _bullets_runs(s["bullets"]), space_after=9, line_spacing=1.02)
    if has_panel:
        px, pw = Inches(8.55), Inches(4.2)
        _box(sl, px, Inches(2.05), pw, Inches(3.6), fill=theme.GREY_LIGHT)
        _box(sl, px, Inches(2.05), Inches(0.10), Inches(3.6), fill=theme.TEAL)
        _text(sl, px + Inches(0.28), Inches(2.25), pw - Inches(0.5), Inches(0.6),
              [[(s["note"]["title"], {"size": 15, "bold": True,
                                      "color": theme.TEAL})]])
        _text(sl, px + Inches(0.28), Inches(2.85), pw - Inches(0.5), Inches(2.6),
              [[(s["note"]["body"], {"size": 14, "color": theme.INK})]],
              line_spacing=1.05)
    _footer(sl, week_no, page)
    return sl


def slide_compare(prs, s, week_no, page):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, theme.PAPER)
    _kicker(sl, s.get("kicker", ""))
    _title(sl, s["title"])
    cols = s["columns"]
    accents = [theme.BLUE, theme.TEAL, theme.AMBER]
    n = len(cols)
    gap = Inches(0.3)
    total = Inches(12.1)
    cw = Emu(int((total - gap * (n - 1)) / n))
    x = Inches(0.6)
    for i, col in enumerate(cols):
        ac = accents[i % len(accents)]
        _box(sl, x, Inches(2.1), cw, Inches(4.7), fill=theme.GREY_LIGHT)
        _box(sl, x, Inches(2.1), cw, Inches(0.7), fill=ac)
        _text(sl, x + Inches(0.2), Inches(2.22), cw - Inches(0.4), Inches(0.5),
              [[(col["head"], {"size": 17, "bold": True, "color": "FFFFFF"})]],
              anchor=MSO_ANCHOR.MIDDLE)
        if col.get("sub"):
            _text(sl, x + Inches(0.2), Inches(2.95), cw - Inches(0.4), Inches(0.5),
                  [[(col["sub"], {"size": 14, "italic": True, "color": ac,
                                  "bold": True})]])
        top = Inches(3.5) if col.get("sub") else Inches(3.0)
        _text(sl, x + Inches(0.2), top, cw - Inches(0.4), Inches(3.0),
              _bullets_runs(col["points"]), space_after=7, line_spacing=1.0)
        x = Emu(int(x + cw + gap))
    _footer(sl, week_no, page)
    return sl


def slide_table(prs, s, week_no, page):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, theme.PAPER)
    _kicker(sl, s.get("kicker", ""))
    _title(sl, s["title"])
    headers = s["headers"]
    rows = s["rows"]
    nrows, ncols = len(rows) + 1, len(headers)
    gt = sl.shapes.add_table(nrows, ncols, Inches(0.6), Inches(2.1),
                             Inches(12.1), Inches(0.5 * nrows)).table
    gt.first_row = False
    for j, h in enumerate(headers):
        c = gt.cell(0, j)
        c.fill.solid(); c.fill.fore_color.rgb = _rgb(theme.NAVY)
        c.text = h
        p = c.text_frame.paragraphs[0]
        p.runs[0].font.size = Pt(14); p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = _rgb("FFFFFF")
    for i, row in enumerate(rows, 1):
        for j, val in enumerate(row):
            c = gt.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = _rgb("FFFFFF" if i % 2 else theme.GREY_LIGHT)
            c.text = str(val)
            p = c.text_frame.paragraphs[0]
            p.runs[0].font.size = Pt(13)
            p.runs[0].font.color.rgb = _rgb(theme.INK)
            if j == 0:
                p.runs[0].font.bold = True
    if s.get("note"):
        _text(sl, Inches(0.6), SH - Inches(1.25), Inches(12.1), Inches(0.8),
              [[(s["note"]["title"] + ":  ", {"size": 14, "bold": True,
                                              "color": theme.TEAL}),
                (s["note"]["body"], {"size": 14, "color": theme.INK})]])
    _footer(sl, week_no, page)
    return sl


def slide_statement(prs, s, week_no, page):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, theme.NAVY)
    _text(sl, Inches(1.0), Inches(1.3), Inches(2), Inches(1.2),
          [[("“", {"size": 80, "bold": True, "color": theme.AMBER})]])
    _text(sl, Inches(1.2), Inches(2.4), Inches(11), Inches(2.2),
          [[(s["quote"], {"size": 32, "bold": True, "color": "FFFFFF",
                          "font": theme.FONT_HEAD})]], line_spacing=1.05)
    if s.get("attribution"):
        _text(sl, Inches(1.2), Inches(5.4), Inches(11), Inches(1.4),
              [[(s["attribution"], {"size": 17, "italic": True,
                                    "color": "C7D2E2"})]], line_spacing=1.05)
    _footer(sl, week_no, page)
    return sl


def slide_steps(prs, s, week_no, page):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, theme.PAPER)
    _kicker(sl, s.get("kicker", ""))
    _title(sl, s["title"])
    steps = s["steps"]
    n = len(steps)
    top = Inches(2.2)
    row_h = Inches(min(0.95, 4.6 / n))
    y = top
    for i, st in enumerate(steps, 1):
        _box(sl, Inches(0.6), y, Inches(0.7), row_h - Inches(0.12),
             fill=theme.BLUE, shape=MSO_SHAPE.OVAL)
        _text(sl, Inches(0.6), y, Inches(0.7), row_h - Inches(0.12),
              [[(str(i), {"size": 20, "bold": True, "color": "FFFFFF"})]],
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        _text(sl, Inches(1.5), y, Inches(11), row_h,
              [[(st["title"] + "  ", {"size": 17, "bold": True,
                                      "color": theme.NAVY}),
                (st.get("body", ""), {"size": 15, "color": theme.INK})]],
              anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
        y = Emu(int(y + row_h))
    if s.get("note"):
        _text(sl, Inches(0.6), SH - Inches(0.95), Inches(12), Inches(0.5),
              [[(s["note"], {"size": 14, "italic": True, "color": theme.GREY})]])
    _footer(sl, week_no, page)
    return sl


def slide_agenda(prs, s, week_no, page):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, theme.PAPER)
    _kicker(sl, "TODAY")
    _title(sl, s["title"])
    items = s["items"]
    half = (len(items) + 1) // 2
    cols = [items[:half], items[half:]]
    x = Inches(0.6)
    for col in cols:
        runs = []
        for it in col:
            runs.append([(it["t"], {"size": 17, "bold": True, "color": theme.BLUE})])
            runs.append([(it["d"], {"size": 14, "color": theme.INK})])
        _text(sl, x, Inches(2.1), Inches(5.9), Inches(4.8), runs,
              space_after=8, line_spacing=1.0)
        x = Inches(6.8)
    _footer(sl, week_no, page)
    return sl


_LAYOUTS = {
    "title": None, "section": None, "content": slide_content,
    "compare": slide_compare, "table": slide_table,
    "statement": slide_statement, "steps": slide_steps, "agenda": slide_agenda,
}


def build_deck(week: dict, out_path: str) -> str:
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH
    page = 0
    for s in week["deck"]:
        t = s["type"]
        if t == "title":
            slide_title(prs, {**s, **{k: week[k] for k in
                       ("number", "title", "block", "subtitle")}})
        elif t == "section":
            slide_section(prs, s, week["number"])
        else:
            page += 1
            _LAYOUTS[t](prs, s, week["number"], page)
    prs.save(out_path)
    return out_path
