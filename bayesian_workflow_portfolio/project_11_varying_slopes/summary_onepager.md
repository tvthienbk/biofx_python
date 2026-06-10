# One-Pager — Dose Response Across Cell Lines (non-technical)

## The question

A drug's readout rises with **dose**, but we tested **8 cell lines** and they are
not interchangeable: they differ in their **baseline** level and in **how steeply**
they respond to dose. We want the typical dose response, the spread across lines,
and — crucially — whether baseline and steepness are **linked**.

## The key finding

**They are linked.** Cell lines with a higher baseline also tend to respond more
steeply to dose (a positive correlation). This matters because it changes how you
predict a *new* line: knowing a new line's baseline tells you something about how
steeply it will respond. A model that treats baseline and steepness as unrelated
would get those predictions wrong.

## What we did right (and the trap we avoided)

We let **both** the baseline and the slope vary by line, **and** we modeled the
**correlation** between them (using an LKJ prior on the correlation). The common
mistake is to let both vary but assume they are independent — that throws away the
link and produces over-confident, biased predictions for new lines.

## What we found

- **Dose raises the readout on average** (positive population slope).
- **Lines differ** in both baseline and steepness — a real, moderate spread.
- **Baseline and steepness are positively correlated** — high-baseline lines
  respond more steeply.

## What to do with this

1. **When predicting a new line's dose response, use the correlation** — do not
   assume a line's baseline and its steepness are unrelated.
2. **Report the population spread**, not just the average: lines genuinely differ.
3. **The correlation estimate is uncertain** because we only have 8 lines; if a
   decision hinges on it, test more lines.

## One caveat worth stating

With only 8 lines, *how strong* the baseline-steepness link is remains uncertain
(the data are consistent with anything from weak to strong positive), and a
skeptical prior would pull the estimate toward "no link". The *direction* (positive)
and the average dose effect are solid; the exact correlation needs more cell lines
to pin down.
