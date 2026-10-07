from __future__ import annotations

from llm import call_structured_llm
from schemas import EvidenceRecord, ExtractedEvidence, SourceDocument
from skill_loader import render_agent_skills


def extract_evidence(
    source: SourceDocument,
    *,
    model: str,
    reviewer_feedback: str | None = None,
) -> EvidenceRecord:
    skills = render_agent_skills("extractor")
    system = f"""You are the data-extraction sub-agent for mitochondrial medicine.
Extract structured evidence only from the supplied source. Do not recommend treatment.
PMID/DOI/NCT/URL provenance is attached by Python after extraction, so do not invent identifiers.

Runtime skills assigned to you:
{skills}
"""
    feedback = ""
    if reviewer_feedback:
        feedback = f"\nReviewer feedback from the previous attempt:\n{reviewer_feedback}\nCorrect only grounded errors."

    extracted = call_structured_llm(
        model=model,
        system_prompt=system,
        user_prompt=f"""SOURCE TITLE: {source.title}
SOURCE TYPE: {source.source_type}
EVIDENCE TRACK: {source.evidence_track}
SOURCE TEXT:
{source.text}
{feedback}
""",
        response_model=ExtractedEvidence,
    )

    return EvidenceRecord(
        **extracted.model_dump(),
        source_type=source.source_type,
        source_id=source.source_id,
        source_url=source.url,
        doi=source.doi,
        evidence_track=source.evidence_track,
    )
