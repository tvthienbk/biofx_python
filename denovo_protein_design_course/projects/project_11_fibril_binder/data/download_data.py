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
# EDIT ONLY THIS for each project. These are the Project 11 inputs: cryo-EM amyloid
# FIBRIL structures (tau PHF + alpha-synuclein fibril) to design against, plus a
# MONOMER model for the conformational-specificity COUNTER-TEST. Treat each
# accession as "candidate — verify on RCSB/UniProt in Week 1" (the catalog flags
# which may be superseded). The fibril-surface HOTSPOTS come from the EXPOSED
# cross-beta surface of these fibrils: isolate a protofilament, keep the ordered
# core, remove waters/heteroatoms, and list the solvent-exposed surface residues as
# your design hotspots (the fibril epitope). The MONOMER is intrinsically disordered
# — pull an AFDB / ensemble model for the counter-test and note the caveat.
# See data/README.md.
# ---------------------------------------------------------------------------
ACCESSIONS: list[Item] = [
    # Tau paired-helical filament (PHF) cryo-EM fibril — CANDIDATE, verify on RCSB in Week 1.
    Item("5O3L", "rcsb", note="candidate tau PHF cryo-EM fibril (Fitzpatrick 2017) — design target surface; epitope from the ordered core"),
    # Item("5O3T", "rcsb", note="candidate tau straight-filament (SF) — cross-check the fibril surface against 5O3L"),
    # Alpha-synuclein cryo-EM fibril — CANDIDATE, verify on RCSB in Week 1 (also the cross-amyloid off-target).
    Item("6CU7", "rcsb", note="candidate alpha-synuclein fibril cryo-EM — alternative target + cross-amyloid off-target"),
    # Item("6H6B", "rcsb", note="candidate alpha-synuclein fibril polymorph — cross-check against 6CU7"),
    #
    # MONOMER models for the conformational-specificity COUNTER-TEST (the disordered monomer of the same
    # protein). The monomer is intrinsically disordered, so a single model is a CAVEAT — prefer an
    # ensemble; the AFDB model is a teaching starting point. Verify the UniProt accessions.
    # Item("P10636", "alphafold", note="Human tau (MAPT) AFDB monomer model (verify) — disordered; counter-test caveat"),
    # Item("P37840", "alphafold", note="Human alpha-synuclein (SNCA) AFDB monomer model (verify) — disordered; counter-test caveat"),
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch project input structures/sequences with provenance.")
    ap.add_argument("--out", default="data", help="output directory (default: data)")
    ap.add_argument("--dry-run", action="store_true", help="print URLs without downloading")
    args = ap.parse_args()
    download_all(ACCESSIONS, args.out, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
