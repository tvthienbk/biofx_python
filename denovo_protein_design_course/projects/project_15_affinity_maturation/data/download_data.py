#!/usr/bin/env python3
"""
download_data.py — reproducible data fetcher for Project 15 (computational antibody affinity maturation).

Copied from templates/download_data.py; ONLY the ACCESSIONS list and this header comment are edited
for this project. The goal is *provenance*: every file that enters the project is logged with its
source URL, an SHA-256 checksum, the fetch date, and a license note.

EDIT-ONLY HEADER (Project 15)
-----------------------------
The single input is ONE antibody-antigen complex from SAbDab (the structural antibody database) that
has a MEASURED KD reported in the literature — that complex is the lead you mature, and its KD is the
baseline every proposed CDR mutation is measured against. ALL accessions are CANDIDATES — verify on
SAbDab/RCSB in Week 1 (structures get superseded), and CONFIRM a published KD exists before committing.

  - <PICK_ON_SABDAB>  (rcsb)  a well-characterized therapeutic Fab-antigen complex WITH a published KD.
                              (candidate — verify on SAbDab/RCSB; the STUDENT picks the complex.)

How to choose (do this in Week 1, do NOT skip):
  1. Browse SAbDab (https://opig.stats.ox.ac.uk/webapps/sabdab) for an antibody-antigen complex whose
     KD/affinity is reported in a primary paper (SAbDab links the literature). A therapeutic Fab-antigen
     complex with a clean single epitope is ideal for teaching.
  2. Confirm the PDB entry is current on RCSB (not superseded) and that the antibody + antigen chains
     are well resolved at the interface (you will read CDR contacts off it).
  3. Record the EXACT KD value + its citation in your problem statement — but do NOT hard-code or assert
     any KD here; this file fetches structures, it does not assert affinities.
  4. Set COMPLEX_PDB below to your chosen accession and uncomment its Item.

Responsible-research note: this is therapeutic-antibody lead optimization against a non-pathogen target;
dual-use risk is low. Keep the target in the therapeutic/diagnostic scope (MASTER_BLUEPRINT.md §7).
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
    os.makedirs(out_dir, exist_ok=True)
    if not items:
        print("  (no accessions set yet — edit the ACCESSIONS list: pick a SAbDab complex WITH a "
              "published KD, verify it, then uncomment its Item.)")
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
        print("REMINDER: open provenance.csv and verify the accession is the complex you intended, "
              "that it is current on RCSB, and that a published KD exists for it.")
    return records


# ---------------------------------------------------------------------------
# EDIT ONLY THIS for each project. Treat each accession as "candidate — verify on
# SAbDab/RCSB in Week 1" (the catalog flags which may be superseded). For THIS project
# the student PICKS the antibody-antigen complex (one WITH a published KD); we ship NO
# default accession on purpose, so nobody silently inherits an unverified complex/KD.
# ---------------------------------------------------------------------------
ACCESSIONS: list[Item] = [
    # PICK ONE on SAbDab (a therapeutic Fab-antigen complex WITH a published KD), verify it on RCSB,
    # then uncomment + set the accession. Example shape (NOT a real recommendation — you choose):
    #
    # Item("XXXX", "rcsb", note="<antibody>-<antigen> Fab complex; published KD in <citation> "
    #                           "(candidate — verify on SAbDab/RCSB; confirm the KD)"),
    #
    # Optional, for the specificity counter-screen (notebook 05): a related off-target antigen
    # (paralog / family member). Add it once you have chosen your primary complex.
    # Item("YYYY", "rcsb", note="related off-target antigen for the specificity panel (verify)"),
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch project input structures/sequences with provenance.")
    ap.add_argument("--out", default="data", help="output directory (default: data)")
    ap.add_argument("--dry-run", action="store_true", help="print URLs without downloading")
    args = ap.parse_args()
    download_all(ACCESSIONS, args.out, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
