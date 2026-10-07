from __future__ import annotations

import json

from llm import call_structured_llm
from schemas import EvidenceRecord, LLMReview, ReviewResult, SourceDocument
from skill_loader import render_agent_skills
from tools.validation import deterministic_evidence_checks


def review_evidence(
    record: EvidenceRecord,
    source: SourceDocument,
    *,
    model: str,
) -> ReviewResult:
    deterministic_issues, quote_verified, sample_size_verified = deterministic_evidence_checks(
        record, source
    )

    skills = render_agent_skills("reviewer")
    system = f"""You are the reviewer-validator LLM sub-agent.
Independently check whether the extraction is scientifically and semantically supported by the source.
You must be conservative: a study objective is not a result, an endpoint is not an effect, and a
pathological mechanism is not a therapeutic benefit. Do not fix the record yourself; return issues
and actionable feedback for the extractor.

Runtime skills assigned to you:
{skills}
"""
    prompt = f"""SOURCE:
{source.text}

EXTRACTED RECORD:
{json.dumps(record.model_dump(), ensure_ascii=False, indent=2)}

DETERMINISTIC GUARDRAIL ISSUES:
{json.dumps(deterministic_issues, ensure_ascii=False)}

Pass only if the claims, study type, numbers, quote, effect classification and intervention semantics
are all defensible from the supplied source. If deterministic issues are present, explain them as well.
"""
    llm_review = call_structured_llm(
        model=model,
        system_prompt=system,
        user_prompt=prompt,
        response_model=LLMReview,
    )

    issues = list(dict.fromkeys([*deterministic_issues, *llm_review.issues]))
    deterministic_passed = not deterministic_issues
    passed = deterministic_passed and llm_review.passed
    feedback = llm_review.feedback_to_extractor
    if issues and not feedback:
        feedback = "; ".join(issues)

    return ReviewResult(
        passed=passed,
        deterministic_passed=deterministic_passed,
        llm_passed=llm_review.passed,
        quote_verified=quote_verified,
        sample_size_verified=sample_size_verified,
        semantic_consistency=llm_review.semantic_consistency,
        issues=issues,
        feedback_to_extractor=feedback,
    )
