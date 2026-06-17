"""RFdiffusion contig strings: parse, build, and validate.

A *contig* tells RFdiffusion which residues are copied verbatim from the input
PDB (the catalytic *motif*) and which residues are generated de novo, plus the
linker lengths between them.  Example used throughout the protocol::

    contigmap.contigs=['10-120,A84-87,10-120']  contigmap.length='150-150'

The protocol (Stage 2, step 6) flags two recurring, campaign-killing mistakes:

* writing a *bare integer* for a generated span (``120``) instead of a range
  (``120-120``); RFdiffusion silently mis-parses some of these, and
* a ``contigmap.length`` that is impossible given the segment ranges.

This module makes both mistakes loud, deterministic errors instead.

The grammar implemented (a faithful subset of RFdiffusion's):

    contigs   := segment ("," segment)*          # one chain
    segment   := motif | gap | break
    motif     := CHAIN START "-" END             # e.g. A84-87  (chain A, 84..87)
    gap       := LO "-" HI                        # e.g. 10-120 (generated span)
    break     := "0"  (after a "/")              # chain break, contributes 0 res

Chain breaks are written ``/0 `` in RFdiffusion; we accept a literal ``/0``
segment as well as the inline ``.../0 ...`` form.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

__all__ = [
    "Segment",
    "MotifSegment",
    "GapSegment",
    "ChainBreak",
    "Contig",
    "ContigError",
    "parse_contig",
    "build_contig",
]


class ContigError(ValueError):
    """Raised when a contig string is malformed or inconsistent."""


@dataclass(frozen=True)
class Segment:
    """Base class for a single comma-separated contig token."""

    def length_range(self) -> Tuple[int, int]:
        """Return ``(min_residues, max_residues)`` contributed by this segment."""
        raise NotImplementedError

    def to_token(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class MotifSegment(Segment):
    """A fixed motif span copied from the input PDB, e.g. ``A84-87``."""

    chain: str
    start: int
    end: int

    def __post_init__(self) -> None:
        if not self.chain.isalpha() or len(self.chain) != 1:
            raise ContigError(f"motif chain must be a single letter, got {self.chain!r}")
        if self.end < self.start:
            raise ContigError(
                f"motif {self.chain}{self.start}-{self.end}: end < start"
            )

    def length_range(self) -> Tuple[int, int]:
        n = self.end - self.start + 1
        return (n, n)

    def to_token(self) -> str:
        return f"{self.chain}{self.start}-{self.end}"


@dataclass(frozen=True)
class GapSegment(Segment):
    """A generated (de novo) span of ``lo``..``hi`` residues, e.g. ``10-120``."""

    lo: int
    hi: int

    def __post_init__(self) -> None:
        if self.lo < 0 or self.hi < 0:
            raise ContigError("generated span lengths must be non-negative")
        if self.hi < self.lo:
            raise ContigError(f"generated span {self.lo}-{self.hi}: hi < lo")

    def length_range(self) -> Tuple[int, int]:
        return (self.lo, self.hi)

    def to_token(self) -> str:
        return f"{self.lo}-{self.hi}"


@dataclass(frozen=True)
class ChainBreak(Segment):
    """A chain break (``/0``); contributes zero residues."""

    def length_range(self) -> Tuple[int, int]:
        return (0, 0)

    def to_token(self) -> str:
        return "/0"


# A motif token looks like  <letter><int>-<int>  (chain is a single A-Z letter).
_MOTIF_RE = re.compile(r"^([A-Za-z])(\d+)-(\d+)$")
# A generated-gap token looks like <int>-<int>.
_GAP_RE = re.compile(r"^(\d+)-(\d+)$")
# A bare integer (the mistake the protocol warns about).
_BARE_INT_RE = re.compile(r"^\d+$")


def _parse_length_spec(length: Optional[str]) -> Optional[Tuple[int, int]]:
    """Parse ``contigmap.length`` like ``'150-150'`` into ``(150, 150)``."""
    if length is None:
        return None
    s = length.strip().strip("'\"")
    if _BARE_INT_RE.match(s):
        n = int(s)
        return (n, n)
    m = _GAP_RE.match(s)
    if not m:
        raise ContigError(f"could not parse contigmap.length={length!r}")
    lo, hi = int(m.group(1)), int(m.group(2))
    if hi < lo:
        raise ContigError(f"contigmap.length {lo}-{hi}: hi < lo")
    return (lo, hi)


def _normalise_contigs(contigs: str) -> str:
    """Strip the Hydra wrapping ``contigmap.contigs=['...']`` down to ``...``."""
    s = contigs.strip()
    if s.startswith("contigmap.contigs="):
        s = s.split("=", 1)[1].strip()
    # strip surrounding [ ] and quotes
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1].strip()
    s = s.strip("'\"")
    return s


@dataclass
class Contig:
    """A parsed contig: an ordered list of segments plus an optional length spec."""

    segments: List[Segment] = field(default_factory=list)
    length: Optional[Tuple[int, int]] = None

    # -- derived quantities -------------------------------------------------
    def length_range(self) -> Tuple[int, int]:
        lo = sum(s.length_range()[0] for s in self.segments)
        hi = sum(s.length_range()[1] for s in self.segments)
        return (lo, hi)

    def motif_segments(self) -> List[MotifSegment]:
        return [s for s in self.segments if isinstance(s, MotifSegment)]

    def motif_residues(self) -> List[str]:
        """Flatten motif spans into per-residue labels, e.g. ``['A84', ...]``."""
        out: List[str] = []
        for m in self.motif_segments():
            out.extend(f"{m.chain}{i}" for i in range(m.start, m.end + 1))
        return out

    # -- validation ---------------------------------------------------------
    def validate(self) -> List[str]:
        """Return a list of human-readable problems; empty list == valid."""
        problems: List[str] = []
        if not self.segments:
            problems.append("contig is empty")
        if not self.motif_segments():
            problems.append(
                "contig contains no motif segment (nothing scaffolds the active site)"
            )
        if self.length is not None:
            lo, hi = self.length_range()
            tlo, thi = self.length
            # The declared total length must be reachable by the segment ranges.
            if thi < lo or tlo > hi:
                problems.append(
                    f"contigmap.length={tlo}-{thi} is impossible: segments allow "
                    f"{lo}-{hi} residues"
                )
        return problems

    def to_contigs_string(self) -> str:
        return ",".join(s.to_token() for s in self.segments)

    def to_hydra(self) -> Tuple[str, Optional[str]]:
        """Return the ``contigmap.contigs=...`` and ``contigmap.length=...`` args."""
        contigs = f"contigmap.contigs=['{self.to_contigs_string()}']"
        length = None
        if self.length is not None:
            lo, hi = self.length
            length = f"contigmap.length='{lo}-{hi}'"
        return contigs, length


def parse_contig(contigs: str, length: Optional[str] = None) -> Contig:
    """Parse a contig string (Hydra-wrapped or bare) into a :class:`Contig`.

    Raises :class:`ContigError` on malformed tokens — notably a bare integer
    where a range is required (the protocol's documented pitfall).
    """
    body = _normalise_contigs(contigs)
    segments: List[Segment] = []
    # tokens are comma separated; "/0" chain breaks may be attached to a token
    raw_tokens: List[str] = []
    for chunk in body.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        # split off any trailing/leading "/0" chain break
        parts = re.split(r"(/0)", chunk)
        for p in parts:
            p = p.strip()
            if p:
                raw_tokens.append(p)

    for tok in raw_tokens:
        if tok == "/0":
            segments.append(ChainBreak())
            continue
        m = _MOTIF_RE.match(tok)
        if m:
            segments.append(
                MotifSegment(chain=m.group(1), start=int(m.group(2)), end=int(m.group(3)))
            )
            continue
        if _BARE_INT_RE.match(tok):
            raise ContigError(
                f"bare integer {tok!r} in contig: generated spans must be a range "
                f"(write {tok}-{tok}, not {tok}). See protocol Stage 2, step 6."
            )
        g = _GAP_RE.match(tok)
        if g:
            segments.append(GapSegment(lo=int(g.group(1)), hi=int(g.group(2))))
            continue
        raise ContigError(f"unrecognised contig token: {tok!r}")

    return Contig(segments=segments, length=_parse_length_spec(length))


def build_contig(
    islands: List[Tuple[str, int, int]],
    flank: Tuple[int, int] = (10, 120),
    inter_island: Optional[Tuple[int, int]] = None,
    total_length: Optional[Tuple[int, int]] = None,
) -> Contig:
    """Build a contig that scaffolds one or more motif ``islands``.

    Each island is ``(chain, start, end)``.  ``flank`` is the generated span
    placed before the first and after the last island; ``inter_island`` (default
    = ``flank``) is placed between consecutive islands.  If ``total_length`` is
    given it is validated against the constructed segments.
    """
    if not islands:
        raise ContigError("need at least one motif island")
    inter = inter_island if inter_island is not None else flank
    segs: List[Segment] = [GapSegment(*flank)]
    for i, (chain, start, end) in enumerate(islands):
        if i > 0:
            segs.append(GapSegment(*inter))
        segs.append(MotifSegment(chain=chain, start=start, end=end))
    segs.append(GapSegment(*flank))
    contig = Contig(segments=segs, length=total_length)
    problems = contig.validate()
    if problems:
        raise ContigError("; ".join(problems))
    return contig
