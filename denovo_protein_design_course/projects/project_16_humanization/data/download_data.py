#!/usr/bin/env python3
"""
download_data.py — shared, reproducible data fetcher for the De Novo Protein Design course.

Every project copies this into its own `data/` folder (or imports it from `shared/`) and
edits only the ACCESSIONS table at the bottom. The goal is *provenance*: every file that
enters a project is logged with its source URL, an SHA-256 checksum, the fetch date, and a
license note, so a thesis can state exactly where each input came from.

Sources
-------
- RCSB PDB structures (mmCIF/PDB)         https://files.rcsb.org/download/{ID}.{cif|pdb}
- AlphaFold DB predicted structures        https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v4.pdb
- UniProt sequences (FASTA)                 https://rest.uniprot.org/uniprotkb/{ACC}.fasta

License notes (record these in your thesis)
-------------------------------------------
- RCSB PDB data are released to the public domain (CC0-equivalent); cite the deposition.
- AlphaFold DB predictions are CC-BY-4.0 (DeepMind/EMBL-EBI); cite Jumper 2021 + Varadi 2022.
- UniProt is CC-BY-4.0.
- Any sequences you curate from a paper's supplementary data inherit that paper's terms —
  log the DOI and check it; some are CC-BY, some are more restrictive.

This script is written to run on Google Colab (it needs network access RCSB/EBI/UniProt).
It is intentionally dependency-light: only the Python standard library + `requests`.

Usage
-----
    python download_data.py                 # fetch everything in ACCESSIONS
    python download_data.py --dry-run       # print what would be fetched
    python download_data.py --out ./data    # choose output dir
Then inspect data/provenance.csv.

EDIT-ONLY HEADER (Project 16 — Antibody Humanization)
-----------------------------------------------------
This project's PRIMARY input is a SEQUENCE, not a structure, so the ACCESSIONS list below is
mostly COMMENTED. You provide:
  (1) a published non-human (murine/chimeric) therapeutic antibody VH + VL sequence — record the
      paper/DOI; place the FASTA in data/inputs/ (tiny, safe to commit). Mark "candidate — verify".
  (2) the HUMAN GERMLINE FRAMEWORK database (IMGT / OAS) — downloaded SEPARATELY (NOT via this
      script, NOT committed): IMGT/GENE-DB germline FRs (academic-use terms; cite Lefranc et al.)
      and, if you score humanness locally, OAS repertoires (large — many GB; document the size).
      For grafting you only need the small germline FR sequences; the large OAS DB is only needed
      for local OASis humanness (BioPhi bundles what it needs).
Use this script only to log provenance of any OPTIONAL structures you pull (e.g., a reference Fab
of your antibody, if one is deposited) — uncomment the example below and verify the PDB ID.
See data/README.md.
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
# EDIT ONLY THIS for each project. For Project 16 the ACCESSIONS list is intentionally
# (almost) EMPTY: the primary input is the student-supplied antibody SEQUENCE (place the
# FASTA in data/inputs/), and the human germline framework DB (IMGT/OAS) is downloaded
# SEPARATELY and never committed (see the EDIT-ONLY header + data/README.md).
# Treat any accession you DO add as "candidate — verify on RCSB/UniProt/SAbDab in Week 1".
# ---------------------------------------------------------------------------
ACCESSIONS: list[Item] = [
    # No structures are fetched by default — the primary input is a SEQUENCE you supply.
    #
    # OPTIONAL: if your chosen non-human antibody has a deposited Fab/Fv structure, uncomment and
    # verify the PDB ID; it is useful for an Fv-model sanity check and to read Vernier positions:
    # Item("XXXX", "rcsb", note="reference Fab/Fv of your antibody — sanity check (candidate — verify)"),
    #
    # OPTIONAL: pull your antibody's VH/VL sequence from UniProt if it has an entry (else use the
    # FASTA from the publication and place it directly in data/inputs/):
    # Item("XXXXXX", "uniprot", note="non-human antibody VH/VL sequence (candidate — verify vs the paper)"),
    #
    # NOTE: the IMGT / OAS human germline framework database is NOT fetched here (large; separate
    # terms). Download it separately per data/README.md and DO NOT commit it.
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch project input structures/sequences with provenance.")
    ap.add_argument("--out", default="data", help="output directory (default: data)")
    ap.add_argument("--dry-run", action="store_true", help="print URLs without downloading")
    args = ap.parse_args()
    download_all(ACCESSIONS, args.out, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
