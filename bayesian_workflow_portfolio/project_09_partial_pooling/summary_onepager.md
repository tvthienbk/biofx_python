# One-Pager — Partial Pooling Across Plates (non-technical)

## The question

We measured an assay readout on **12 plates**, with only **4 wells per plate**.
How different are the plates really, and what is the best estimate for each one?

## The trap we avoided

Two tempting shortcuts are both wrong:

- **Treat every plate separately.** With only 4 wells each, a plate's average is
  noisy — one odd well swings it. You will "discover" plate differences that are
  just measurement noise.
- **Pool everything into one grand average.** This pretends all plates are
  identical and hides real plate-to-plate variation.

We used **partial pooling**, the principled middle ground. Each plate's estimate
is pulled toward the overall average by an amount the data decide — pulled *more*
when a plate has few or noisy wells, *less* when its signal is strong.

## What we found

- **Overall mean readout:** about **5.0** (tight uncertainty).
- **Plate-to-plate variation:** the between-plate spread is about **0.8** — real,
  but modest. Plates do differ, but not wildly.
- **Best per-plate estimates:** the *shrunken* values, not the raw 4-well
  averages. The raw averages overstate how different the plates are.

## What to do with this

1. **Report the shrunken per-plate estimates**, not the raw averages — especially
   for plates flagged as outliers on raw data; several of those move back toward
   the pack once noise is accounted for.
2. **Budget for the real plate variation (~0.8)** in downstream decisions; it is
   not zero, so a single plate is not a perfect stand-in for all.
3. **If you need sharper per-plate numbers, add wells, not plates** — the
   uncertainty here is driven by *few observations per plate*.

## One caveat worth stating

With only 12 plates, the estimate of *how much* plates vary (the 0.8) is itself
uncertain and somewhat sensitive to modeling choices. The overall mean is solid;
treat the spread as "modest, probably near 0.8" rather than an exact figure. If a
decision hinges on that spread, collect more plates.
