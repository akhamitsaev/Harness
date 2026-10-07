from __future__ import annotations

import json

from llm import call_structured_llm
from schemas import ComparisonBundle, EvidenceRecord, SearchPlan
from skill_loader import render_agent_skills


def compare_with_standard(
    evidence: list[EvidenceRecord],
    search_plan: SearchPlan,
    *,
    model: str,
) -> ComparisonBundle:
    skills = render_agent_skills("comparator")
    system = f"""You are the analyst-comparator LLM sub-agent.
Compare mitochondrial-targeted directions with the traditional/standard-of-care evidence for the
same disease. Use ONLY reviewer-passed evidence supplied to you. Never infer a head-to-head efficacy
advantage when the studies are not directly comparable. If evidence is insufficient, say so.

Runtime skills assigned to you:
{skills}
"""
    compact = [
        {
            "source_id": r.source_id,
            "track": r.evidence_track,
            "intervention": r.intervention,
            "disease": r.disease,
            "study_type": r.study_type,
            "evidence_level": r.evidence_level,
            "phase": r.phase,
            "n": r.n,
            "outcome": r.outcome,
            "effect": r.effect,
            "effect_class": r.effect_class,
        }
        for r in evidence
    ]
    prompt = f"""Configured standard of care: {search_plan.standard_of_care}

Reviewer-passed evidence:
{json.dumps(compact, ensure_ascii=False, indent=2)}

Create comparisons for mitochondrial interventions for which there is usable evidence. Supporting
source IDs must come from the supplied evidence only.
"""
    return call_structured_llm(
        model=model,
        system_prompt=system,
        user_prompt=prompt,
        response_model=ComparisonBundle,
    )
