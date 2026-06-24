# Project 14 — Reading List

Tiered. Read **Tier 1** in Week 1, **Tier 2** as you build, **Tier 3** for depth/MSc track.
Cite the exact versions of any tool you actually run.

## Tier 1 — essential (read before Week 3)
- **Bennett et al. 2025, *Nature* (RFantibody)** — the core tool: de novo antibody/VHH CDR design
  (RFdiffusion-Ab + ProteinMPNN). Read for: the method, and the **low** experimental hit rate (why you screen).
- **Abanades et al. 2023 (ImmuneBuilder)** — fast antibody/nanobody structure prediction (NanoBodyBuilder2);
  read for: antibody-aware CDR geometry without an MSA.
- **A HA-stem or RSV-F prefusion immunogen paper (e.g. McLellan / DS-Cav1)** — read for: what makes an
  epitope **conserved + neutralizing**, the rationale for the target face.

## Tier 2 — build-time references
- **BoltzGen 2025** — alternative de novo nanobody generator for the head-to-head (verify release).
- **Evans et al. 2021 (AlphaFold-Multimer)** — `pae_interaction` and interface confidence, the key complex metric.
- **Raybould et al. 2019 (TAP, Therapeutic Antibody Profiler)** — developability flags (what the heuristics imitate).
- **Dauparas et al. 2022 (ProteinMPNN)** — CDR-loop sequence design over the diffused backbones.

## Tier 3 — depth
- **Broadly-neutralizing-antibody literature (HA stem / RSV F)** — context for designing for breadth across strains.
- **Yeast/phage display methods** — for the screen plan (how low-hit-rate pools become real binders).
- **Pseudovirus neutralization assay methods** — for the validation plan (the standard, biosafe surrogate).

## How to use these in your report
- Methods: cite the tool papers + versions; state the epitope + framework + their conservation evidence.
- Results: report the survival-at-each-layer hit rate, the developability gate, **and** the cross-strain breadth (worst-case).
- Responsible research: cite §7; state the defensive (neutralizing) framing + the biosafety oversight for validation.
