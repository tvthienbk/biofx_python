# Project 07 — Technical Manual

The reference companion to `INSTRUCTIONS.md`. Read the relevant section before each phase.

## 1. Background theory
A de novo binder is a small protein designed to bind a chosen surface (epitope) of a target. Here the
target is the SARS-CoV-2 spike **RBD**, and the chosen epitope is the **ACE2-binding (host-receptor)
face** — a binder that occludes it **blocks** the virus (neutralization by competition). Two
paradigms: **BindCraft** (one-shot hallucination with AF2-Multimer in the loop) and **RFdiffusion
binder mode** (diffuse a backbone against hotspots → ProteinMPNN sequence → AF2-Multimer
re-prediction). The key confidence metric for a complex is **AF2-Multimer `pae_interaction`** (the
predicted aligned error across the binder–target interface; lower is better), complemented by interface
pLDDT, self-consistency scRMSD, and shape complementarity.

The project-specific hard problem is **breadth**: the RBM mutates fast, so a binder to a variable
epitope escapes quickly. Targeting a **conserved** epitope (low sequence variation across
sarbecoviruses/variants) trades some affinity for variant-resistance. You quantify breadth by modeling
each binder against a **panel** of variant RBDs and reporting the **worst-case** `pae_interaction`.

Why this is hard and what realistic success looks like: de novo binder hit rates are variable and
often low, and **breadth is harder than affinity**; predicted metrics enrich but do not guarantee. A
realistic outcome is a small, honestly-characterized set of conserved-epitope candidates with a
predicted-breadth profile and a controlled plan to test them — not a finished antiviral.

## 2. Tools used (exact versions pinned in `env/requirements.txt`)

### BindCraft (or FreeBindCraft)
- **What/where:** one-shot binder hallucination with AF2-Multimer in the loop; paradigm #1.
- **Install:** `https://github.com/martinpacesa/BindCraft` (pin a commit). Free-tier fallback: `https://github.com/cytokineking/FreeBindCraft` (**verify it still exists**).
- **Key params:** `target_pdb` (cleaned RBD), `hotspot_residues` (the conserved ACE2-face epitope), `binder_length`, `num_designs`.
- **Compute:** A100 strongly recommended; free T4 → FreeBindCraft + small `num_designs` only.

### RFdiffusion binder mode + ProteinMPNN
- **What/where:** diffuse a backbone against hotspots, then design its sequence; paradigm #2.
- **Install:** RFdiffusion `https://github.com/RosettaCommons/RFdiffusion`; ColabDesign `https://github.com/sokrypton/ColabDesign` (binder protocol + ProteinMPNN). Pin commits.
- **Key params:** `ppi.hotspot_res` (epitope), `binderlen`, ProteinMPNN `temperature`, `num_seq_per_backbone`.
- **Compute:** 500–1000 backbones want A100/HPC; small batches OK on T4.

### AF2-Multimer (ColabFold)
- **What/where:** re-predict each (binder, RBD) complex → `pae_interaction` (THE key binder metric) + interface pLDDT.
- **Install:** `https://github.com/sokrypton/ColabFold` (pin a commit). Small complexes OK on T4; campaign-scale prefers A100. Usually the slow step — batch overnight.

### Conservation / breadth analysis
- Align a panel of RBD variant sequences (e.g. MAFFT), score epitope conservation, and re-run AF2-Multimer per variant. The `binder_tools.py` helpers `epitope_conservation()` and `breadth_across_variants()` scaffold this.

## 3. The pipeline, step by step
```
00_setup            → GPU check + installs (graceful T4 fallback)
01_define_explore   → clean RBD, map the conserved epitope + hotspots, metrics table, mock hello-world
02_generate         → BindCraft (50–200) + RFdiffusion (500–1000 → MPNN → AF2-Multimer) campaign
03_filter_and_rank  → shared/filtering_pipeline.py (design_type="binder") → ranked CSV + survival figure
04_validate         → cross-variant BREADTH (pae across variants) + conserved-vs-variable + head-to-head
05_validation_plan  → SPR/BLI + ACE2-competition + pseudovirus-neutralization breadth plan (with controls + IBC)
```

## 4. Filtering cutoffs for this design type (binder)
| Metric | Cutoff | Why |
|--------|--------|-----|
| scRMSD | < 2.5 Å | self-consistency (designed vs predicted binder backbone) |
| pLDDT | > 80 | interface/local confidence (NOT affinity) |
| pae_interaction | < 10 Å | interface confidence — the key binder metric |
| rosetta_dG | < −30 REU | interface energy (PyRosetta/FreeBindCraft relax) |
| shape complementarity | > 0.6 | packing across the interface |
| **worst-case breadth pae** | report it | a broad neutralizer keeps low pae across ALL variants |

> Reminder: **no in-silico metric perfectly separates true from false binders.** Filters enrich; they
> do not guarantee. Breadth is harder than affinity — report the worst variant, not the best.

## 5. Interpreting results
- A *promising* binder: low `pae_interaction` + low scRMSD + good shape complementarity + covers the ACE2 footprint + **stays low-pae across the variant panel**.
- A *suspicious* one: low pae on the design variant but high pae on others (narrow, escape-prone), or high pLDDT with high scRMSD (confident wrong fold).
- **Breadth profile:** plot each candidate's pae across the variant panel; the worst-case value ranks breadth.
- **Hit rate:** report N pass / N generated at each layer, per paradigm — the honest accounting.

## 6. Troubleshooting
| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Colab OOM / dies | campaign too large for T4 | FreeBindCraft + small `num_designs`; batch; move to A100 |
| Upstream install fails | repo/notebook changed | use the pinned commit; update install cell; log it |
| All designs fail self-consistency | bad target prep / wrong chain | re-clean the RBD; check epitope residue numbering; lower MPNN temperature |
| Binder great on one variant, bad on others | targeted a variable epitope | re-map to a more conserved epitope; re-run breadth |
| pae_interaction looks random | AF2-Multimer parsing error | confirm multimer model; parse inter-chain PAE correctly |

## 7. Experimental validation reference (for the D4 plan)
- Expression: *E. coli* BL21(DE3) for small binders; note when mammalian expression is needed.
- Characterization: go/no-go (express → SDS-PAGE → SEC) → SPR/BLI vs RBD → **ACE2-competition** → **pseudovirus neutralization** across the variant panel (standard BSL-2 surrogate; **IBC approval required**).
- **Controls:** positive (a known neutralizing binder/nanobody), negative (scrambled-interface), unrelated-antigen negative. Report breadth as worst-case across the panel.
- **Biosafety:** pseudovirus assays and any work touching viral material require institutional biosafety committee (IBC) approval at the appropriate containment level. Authentic-virus neutralization is higher-containment and out of scope for most courses — pseudovirus is the standard, safe surrogate.

## 8. Responsible research
**Defensive / neutralizing only.** In scope: blocking the virus by occluding the ACE2-binding face of
a conserved epitope (antiviral/diagnostic). Out of scope: enhancing transmissibility, virulence,
receptor affinity, immune escape, or any pathogen gain-of-function. See `MASTER_BLUEPRINT.md §7`.
Synthesis screening + IBC/institutional approval required for any wet-lab work. Never overstate results.

## 9. Key references
See `references/reading_list.md`. Cite the exact tool papers and versions you actually used.
