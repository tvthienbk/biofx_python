"""
predict.py — unified structure-prediction wrapper for Project 01.

Goal: one function, `predict(sequence, tool)`, that runs ESMFold / ColabFold(AF2) / Boltz-2 and
returns a uniform record `{tool, pdb_path, plddt, pae, ptm, runtime_s}`. The notebooks import this
so the logic is testable and the notebooks stay thin.

DESIGN NOTE FOR STUDENTS
------------------------
Real model loading is heavy and environment-specific, so each backend is implemented as a small
adapter you complete/verify on Colab (the heavy import happens *inside* the function, lazily). The
module is import-safe with NO GPU and NO heavy packages installed: it will import fine here; the
backends raise a clear, actionable error if their dependency is missing. There is also a
`MockBackend` so you can develop and unit-test the *plumbing* (parsing, records, aggregation)
before you spend GPU time.

Fill in / verify the TODOs against the current ColabFold / transformers / Boltz APIs at the start
of the course (these libraries change — pin versions and log them).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Prediction:
    tool: str
    sequence: str
    pdb_path: Optional[str] = None
    plddt: Optional[float] = None        # mean pLDDT (0–100)
    pae: Optional[float] = None          # mean / interaction PAE (Å)
    ptm: Optional[float] = None
    runtime_s: Optional[float] = None
    ok: bool = True
    error: Optional[str] = None

    def as_row(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Backends. Each returns a Prediction. Heavy imports are LAZY (inside the call).
# --------------------------------------------------------------------------- #
def _esmfold(sequence: str, out_dir: str = "results/esmfold") -> Prediction:
    """ESMFold via HuggingFace transformers. T4 OK for <~400 aa."""
    t0 = time.time()
    try:
        import os
        import torch  # noqa: F401
        from transformers import AutoTokenizer, EsmForProteinFolding
    except ImportError as e:
        return Prediction("esmfold", sequence, ok=False,
                          error=f"missing dep ({e}); run install_esmfold() in 00_setup")
    try:
        import os, torch
        os.makedirs(out_dir, exist_ok=True)
        tok = AutoTokenizer.from_pretrained("facebook/esmfold_v1")
        model = EsmForProteinFolding.from_pretrained("facebook/esmfold_v1")
        model = model.eval()
        if torch.cuda.is_available():
            model = model.cuda()
        inputs = tok([sequence], return_tensors="pt", add_special_tokens=False)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        with torch.no_grad():
            out = model(**inputs)
        plddt = float(out["plddt"].mean().item())
        pdb_path = os.path.join(out_dir, "esmfold.pdb")
        # TODO: write the PDB from `out` using the model's to_pdb helper for your transformers version.
        return Prediction("esmfold", sequence, pdb_path=pdb_path, plddt=plddt,
                          runtime_s=round(time.time() - t0, 1))
    except Exception as e:  # noqa: BLE001
        return Prediction("esmfold", sequence, ok=False, error=repr(e),
                          runtime_s=round(time.time() - t0, 1))


def _colabfold(sequence: str, out_dir: str = "results/af2") -> Prediction:
    """AlphaFold2 via ColabFold. Verify the current API/notebook and pin the commit."""
    t0 = time.time()
    try:
        # TODO: import/run the ColabFold batch API you installed in 00_setup.
        # The most robust route on Colab is often the official ColabFold notebook's
        # colabfold_batch; wrap it here and parse pLDDT/PAE/pTM from the output JSON.
        raise NotImplementedError(
            "Wire up ColabFold here. Run install_colabfold() in 00_setup, then call "
            "colabfold_batch on a FASTA and parse the result JSON for pLDDT/PAE/pTM.")
    except Exception as e:  # noqa: BLE001
        return Prediction("af2", sequence, ok=False, error=repr(e),
                          runtime_s=round(time.time() - t0, 1))


def _boltz(sequence: str, out_dir: str = "results/boltz") -> Prediction:
    """Boltz-2. Heavier; small monomers OK on T4, complexes/affinity prefer A100."""
    t0 = time.time()
    try:
        raise NotImplementedError(
            "Wire up Boltz-2 here. `pip install boltz`, build the input YAML, run boltz predict, "
            "parse confidence (and affinity for the stretch task).")
    except Exception as e:  # noqa: BLE001
        return Prediction("boltz", sequence, ok=False, error=repr(e),
                          runtime_s=round(time.time() - t0, 1))


def _mock(sequence: str, out_dir: str = "results/mock") -> Prediction:
    """Deterministic fake backend so you can develop the plumbing with no GPU.
    NEVER present mock numbers as real results — they are synthetic by construction."""
    import hashlib
    h = int(hashlib.sha256(sequence.encode()).hexdigest(), 16)
    plddt = 50 + (h % 50)            # 50–99
    pae = 5 + (h % 20)               # 5–24
    return Prediction("mock", sequence, pdb_path=None, plddt=float(plddt),
                      pae=float(pae), ptm=round((plddt / 100), 3), runtime_s=0.0,
                      error="SYNTHETIC — mock backend, not a real prediction")


_BACKENDS = {"esmfold": _esmfold, "af2": _colabfold, "colabfold": _colabfold,
             "boltz": _boltz, "mock": _mock}


def predict(sequence: str, tool: str = "esmfold", **kwargs) -> Prediction:
    """Run one predictor. tool ∈ {esmfold, af2/colabfold, boltz, mock}."""
    tool = tool.lower()
    if tool not in _BACKENDS:
        raise ValueError(f"unknown tool {tool!r}; options: {sorted(_BACKENDS)}")
    if not sequence or any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in sequence.upper()):
        return Prediction(tool, sequence, ok=False, error="invalid amino-acid sequence")
    return _BACKENDS[tool](sequence.upper(), **kwargs)


def predict_all(sequence: str, tools=("esmfold", "af2", "boltz")) -> list[Prediction]:
    """Run several predictors and return their records (for AF2/ESMFold/Boltz agreement)."""
    return [predict(sequence, t) for t in tools]


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps).
    seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ"
    for p in predict_all(seq, tools=("mock",)):
        print(p.as_row())
