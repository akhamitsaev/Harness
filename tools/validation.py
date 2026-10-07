from __future__ import annotations

import re

from schemas import EvidenceRecord, SourceDocument


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def deterministic_evidence_checks(
    record: EvidenceRecord,
    source: SourceDocument,
) -> tuple[list[str], bool, bool]:
    """Hard guardrails complementing the LLM reviewer.

    These checks are intentionally mechanical: provenance, verbatim quote and explicit n.
    Semantic judgment is delegated to the LLM reviewer.
    """
    issues: list[str] = []

    if record.source_id != source.source_id:
        issues.append("Source ID mismatch")
    if record.source_url != source.url:
        issues.append("Source URL mismatch")
    if record.source_type != source.source_type:
        issues.append("Source type mismatch")
    if record.doi != source.doi:
        issues.append("DOI mismatch")
    if record.evidence_track != source.evidence_track:
        issues.append("Evidence track mismatch")

    quote_verified = bool(
        record.source_quote
        and _norm(record.source_quote) in _norm(source.text)
    )
    if not quote_verified:
        issues.append("source_quote is missing or not found verbatim in source text")

    sample_size_verified = True
    if record.n is not None:
        sample_size_verified = bool(
            re.search(rf"(?<!\d){record.n}(?!\d)", source.text)
        )
        if not sample_size_verified:
            issues.append(f"Sample size n={record.n} was not found in source text")

    return issues, quote_verified, sample_size_verified
