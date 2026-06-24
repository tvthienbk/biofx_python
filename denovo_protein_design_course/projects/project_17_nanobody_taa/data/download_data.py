#!/usr/bin/env python3
"""
download_data.py — reproducible data fetcher for Project 17 (nanobody vs a tumor-associated antigen).

Copied from templates/download_data.py; ONLY the ACCESSIONS list and this header comment are edited
for this project. The goal is *provenance*: every file that enters the project is logged with its
source URL, an SHA-256 checksum, the fetch date, and a license note.

EDIT-ONLY HEADER (Project 17)
-----------------------------
Inputs are the tumor-associated antigen (TAA) structures you design VHH/nanobodies against, plus the
related-receptor panel for the specificity counter-screen. ALL accessions are CANDIDATES — verify on
RCSB in Week 1 (structures get superseded). The catalog flags these as candidates.

  - 1N8Z  (rcsb)  trastuzumab Fab - HER2 (ERBB2) domain IV complex. HER2 is the primary TAA; the
                  trastuzumab footprint defines the "overlapping" epitope option.  (candidate — verify)
  - 1IVO  (rcsb)  EGFR (ERBB1) extracellular region + EGF. Alternative TAA AND a receptor-family
                  off-target for the HER-family specificity panel.               (candidate — verify)

Mesothelin: there is no single canonical experimental TAA-epitope structure as clean as 1N8Z/1IVO for
teaching; if you choose mesothelin, build/obtain a structural MODEL (e.g., an AlphaFold DB model via
the AFDB source, UniProt Q13421) and mark it "model — verify". Do NOT treat a model as an experimental
structure.

Receptor-family specificity panel (for the counter-screen in notebooks 04/05): the HER/ErbB family —
HER2 (target), EGFR/HER1, HER3 (ERBB3), HER4 (ERBB4). Add HER3/HER4 structures or AFDB models when you
build the panel; verify each accession at course start. Keep the panel to relatives that share surface
with your epitope so the specificity test is meaningful.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import requests
except ImportError:  # pragma: no cover
    print("This script needs `requests`. On Colab: !pip -q install requests", file=sys.stderr)
    raise

RCSB_URL = "https://files.rcsb.org/download/{id}.{ext}"
AFDB_URL = "https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v4.pdb"
UNIPROT_FASTA_URL = "https://rest.uniprot.org/uniprotkb/{acc}.fasta"

LICENSE_BY_SOURCE = {
    "rcsb": "Public domain (PDB); cite the deposition.",
    "alphafold": "CC-BY-4.0 (AlphaFold DB); cite Jumper 2021 + Varadi 2022.",
    "uniprot": "CC-BY-4.0 (UniProt).",
}


@dataclass
class Item:
    """One thing to fetch."""
    accession: str
    source: str                 # "rcsb" | "alphafold" | "uniprot"
    ext: str = "cif"            # for rcsb: "cif" (preferred) or "pdb"
    note: str = ""              # why this file is in the project
    filename: Optional[str] = None  # override the saved filename

    def url(self) -> str:
        if self.source == "rcsb":
            return RCSB_URL.format(id=self.accession.upper(), ext=self.ext)
        if self.source == "alphafold":
            return AFDB_URL.format(acc=self.accession.upper())
        if self.source == "uniprot":
            return UNIPROT_FASTA_URL.format(acc=self.accession.upper())
        raise ValueError(f"unknown source: {self.source}")

    def default_filename(self) -> str:
        if self.source == "rcsb":
            return f"{self.accession.upper()}.{self.ext}"
        if self.source == "alphafold":
            return f"AF-{self.accession.upper()}-F1-model_v4.pdb"
        if self.source == "uniprot":
            return f"{self.accession.upper()}.fasta"
        return self.accession


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(item: Item, out_dir: str, retries: int = 3, timeout: int = 60) -> dict:
    """Download one item, write it, and return a provenance record."""
    os.makedirs(out_dir, exist_ok=True)
    fname = item.filename or item.default_filename()
    dest = os.path.join(out_dir, fname)
    url = item.url()

    if os.path.exists(dest):
        digest = sha256_of(dest)
        print(f"  [cached] {fname}  sha256={digest[:12]}…")
        return _record(item, url, dest, digest, status="cached")

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200 and resp.content:
                with open(dest, "wb") as fh:
                    fh.write(resp.content)
                digest = sha256_of(dest)
                print(f"  [ok] {fname}  ({len(resp.content)} bytes)  sha256={digest[:12]}…")
                return _record(item, url, dest, digest, status="downloaded")
            last_err = f"HTTP {resp.status_code}"
        except Exception as exc:  # noqa: BLE001
            last_err = repr(exc)
        time.sleep(2 * attempt)
    print(f"  [FAIL] {fname}  ({last_err})  url={url}", file=sys.stderr)
    return _record(item, url, dest, "", status=f"failed:{last_err}")


def _record(item: Item, url: str, dest: str, digest: str, status: str) -> dict:
    return {
        "accession": item.accession.upper(),
        "source": item.source,
        "filename": os.path.basename(dest),
        "url": url,
        "sha256": digest,
        "status": status,
        "license": LICENSE_BY_SOURCE.get(item.source, "UNKNOWN — check before use"),
        "note": item.note,
        "fetched_utc": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def write_provenance(records: list[dict], out_dir: str) -> str:
    path = os.path.join(out_dir, "provenance.csv")
    cols = ["accession", "source", "filename", "url", "sha256",
            "status", "license", "note", "fetched_utc"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in records:
            w.writerow(r)
    return path


def download_all(items: list[Item], out_dir: str, dry_run: bool = False) -> list[dict]:
    print(f"Fetching {len(items)} item(s) into {out_dir!r}")
    records = []
    for it in items:
        if dry_run:
            print(f"  [dry-run] would fetch {it.url()}")
            continue
        records.append(fetch(it, out_dir))
    if not dry_run:
        p = write_provenance(records, out_dir)
        ok = sum(r["status"] in ("downloaded", "cached") for r in records)
        print(f"\nDone: {ok}/{len(records)} succeeded. Provenance → {p}")
        print("REMINDER: open provenance.csv and verify every accession is the one you "
              "intended; PDB entries are occasionally superseded.")
    return records


# ---------------------------------------------------------------------------
# EDIT ONLY THIS for each project. Treat each accession as "candidate — verify on
# RCSB/UniProt in Week 1" (the catalog flags which may be superseded).
# ---------------------------------------------------------------------------
ACCESSIONS: list[Item] = [
    Item("1N8Z", "rcsb", note="trastuzumab Fab - HER2 domain IV — primary TAA; defines the "
                              "overlapping epitope (candidate — verify on RCSB)"),
    Item("1IVO", "rcsb", note="EGFR extracellular region + EGF — alternative TAA AND HER-family "
                              "off-target for the specificity panel (candidate — verify on RCSB)"),
    # Mesothelin option: no clean experimental TAA-epitope structure for teaching — use an AFDB MODEL
    # and mark it "model — verify". Uncomment to pull the AlphaFold model for UniProt Q13421:
    # Item("Q13421", "alphafold", note="mesothelin (MSLN) AFDB MODEL — verify; treat as a model, "
    #                                  "NOT an experimental structure"),
    #
    # Receptor-family specificity panel (add HER3/HER4 structures or AFDB models when you build the
    # counter-screen; verify each). EGFR (1IVO) above already serves as one HER-family off-target.
    # Item("P21860", "alphafold", note="HER3 (ERBB3) AFDB MODEL — specificity off-target (verify)"),
    # Item("Q15303", "alphafold", note="HER4 (ERBB4) AFDB MODEL — specificity off-target (verify)"),
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch project input structures/sequences with provenance.")
    ap.add_argument("--out", default="data", help="output directory (default: data)")
    ap.add_argument("--dry-run", action="store_true", help="print URLs without downloading")
    args = ap.parse_args()
    download_all(ACCESSIONS, args.out, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
