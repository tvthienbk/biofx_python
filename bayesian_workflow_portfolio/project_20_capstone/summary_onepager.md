# One-Pager — Which Compound Should We Advance? (Project 20)

**Audience:** a project lead who must pick one compound to take forward from a noisy
screen, and wants a defensible recommendation -- not a statistics seminar.

## The question

We screened a set of candidate compounds. Some were tested many times, some only
two or three. We must advance **one**. Which one -- and how sure are we?

## The trap we avoided

The obvious move -- "advance the one with the highest average" -- is wrong here. A
compound tested only twice can post a high average **by luck**. In this screen the
raw-average "winner" was tested just twice; the genuinely best compound was a
different one. Picking the lucky winner would waste the program's next phase on a
fluke. This is the well-known **winner's curse** of small samples.

## What we did

We fit a model that **borrows strength across compounds**: it recognises that a
high average from two measurements is less trustworthy than the same average from
twenty, and it pulls the under-tested compounds' estimates toward the overall
average accordingly. Then -- and this is the key step -- we did not stop at the
estimates. We wrote down what we actually care about (advancing a truly good
compound) and computed, for each candidate:

- its **expected value** if advanced,
- the **probability it is genuinely the best**, and
- its **expected regret** (how much we'd lose, on average, versus a perfect choice).

We recommend the compound with the **lowest expected regret**.

## What we found

- The recommendation **corrects the winner's curse**: it advances a well-supported
  compound, not the lucky low-sample one.
- The "probability of being best" is spread across a few candidates -- an honest
  signal that the screen is noisy.

## What you can do with it

- **Advance the recommended compound** -- it is the choice that minimises expected
  loss given everything we know.
- Because no single compound dominates, **consider carrying the runner-up too**, or
  **running more replicates** on the close contenders before committing.
- The recommendation is stable under reasonable modelling choices; we checked.

## Bottom line

We turned a noisy screen into an explicit, defensible decision -- correcting for the
small-sample winner's curse and accounting for uncertainty -- rather than stopping at
a table of averages. Advance the recommended compound, and decide whether the
remaining ambiguity is worth resolving with more data before the next phase.
