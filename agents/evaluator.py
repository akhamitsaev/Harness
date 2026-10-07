from __future__ import annotations

import json

from llm import call_structured_llm
from schemas import AssessmentBundle, ComparisonBundle, EvidenceRecord, SearchPlan
from skill_loader import render_agent_skills


def evaluate_promisingness(
    evidence: list[EvidenceRecord],
    comparisons: ComparisonBundle,
    search_plan: SearchPlan,
    *,
    model: str,
) -> AssessmentBundle:
    skills = render_agent_skills("evaluator")
    system = f"""You are the promisingness-evaluator LLM sub-agent.
Your job is to assign a transparent research-priority score, not to give clinical advice.
Score therapeutic directions only from reviewer-passed evidence and comparator analysis. Apply the
runtime rubric exactly, penalize weak/preclinical evidence, and state limitations explicitly.

Runtime skills assigned to you:
{skills}
"""
    compact = [
        {
            "source_id": r.source_id,
            "track": r.evidence_track,
            "intervention": r.intervention,
            "study_type": r.study_type,
            "evidence_level": r.evidence_level,
            "phase": r.phase,
            "n": r.n,
            "effect": r.effect,
            "effect_class": r.effect_class,
        }
        for r in evidence
        if r.intervention
    ]
    prompt = f"""Disease: {search_plan.disease}
Standard of care: {search_plan.standard_of_care}

Reviewer-passed therapeutic evidence:
{json.dumps(compact, ensure_ascii=False, indent=2)}

Comparator output:
{json.dumps(comparisons.model_dump(), ensure_ascii=False, indent=2)}

Return one assessment per distinct therapeutic direction with evidence. Include both mitochondrial
and standard-of-care directions when present. supporting_source_ids must be drawn from the supplied evidence.
"""
    return call_structured_llm(
        model=model,
        system_prompt=system,
        user_prompt=prompt,
        response_model=AssessmentBundle,
    )
